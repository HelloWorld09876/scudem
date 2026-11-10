import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
OUT = ROOT / "paper" / "generated" / "numbers.tex"


BASE_TOL = 100e3        # baseline pressure tolerance in Pa (config/baseline.toml)


def load(name):
    return json.loads((RES / f"{name}.json").read_text())


def fmt(x, d=1):
    return "--" if x is None else f"{x:.{d}f}"


g, s, d, w = load("01_growth"), load("02_static_model"), load("03_lifting_dynamics"), load("04_socket_over_growth")
r, c, u = load("05_replacement_policy"), load("06_window_closure"), load("07_uncertainty")
m, v = load("08_musculoskeletal"), load("09_verification")
k = load("11_closure_sensitivity")["cases"]
t = d["tasks"]
hd, cp, ode, val = load("13_headroom_law"), load("14_closure_probability"), load("15_ode_formulation"), load("16_validation")
ha = load("12_closure_hidden_assumptions")
A, B = cp["A"], cp["B"]
tab = hd["table"]
tplus = [v["T"]["0.25"] for v in tab.values()]
va, vb, vc, vd = val["A_replacement_interval"], val["B_pain_threshold"], val["D_girth"], val["C_growth_share"]
oos = [v["rmse_cm"] for v in val["F_growth_out_of_sample"].values()]


def sci(x, d_=0):
    """Scientific notation as a LaTeX math fragment, e.g. 6e-08 -> 6\\times10^{-8}."""
    mant, exp = f"{x:.{d_}e}".split("e")
    return f"{mant}\\times10^{{{int(exp)}}}"


macros = {
    "pbRmseBoy": fmt(g["boy"]["rmse_cm"], 2), "pbRmseGirl": fmt(g["girl"]["rmse_cm"], 2),
    "phvBoy": fmt(g["boy"]["phv_cm_per_yr"]), "phvAgeBoy": fmt(g["boy"]["phv_age"]),
    "phvGirl": fmt(g["girl"]["phv_cm_per_yr"]), "phvAgeGirl": fmt(g["girl"]["phv_age"]),
    "pbThetaBoy": fmt(g["boy"]["theta"], 2), "pbThetaGirl": fmt(g["girl"]["theta"], 2),
    "pbSzeroBoy": fmt(g["boy"]["s0"], 3), "pbSoneBoy": fmt(g["boy"]["s1"], 3),
    "pbHoneBoy": fmt(g["boy"]["h1"]), "pbHoneGirl": fmt(g["girl"]["h1"]),
    "slopeFixed": fmt(s["boy"]["slope_fixed"], 3), "slopeObject": fmt(s["boy"]["slope_object_term"], 3),
    "leadingError": fmt(100 * s["boy"]["max_rel_error_leading"], 0),
    "staticEight": fmt(s["boy_age8_static_kPa"]),
    "pHold": fmt(t["Static hold"]["peak_pressure_kPa"]), "pSlow": fmt(t["Slow curl"]["peak_pressure_kPa"]),
    "pFast": fmt(t["Fast curl"]["peak_pressure_kPa"]), "pShelf": fmt(t["Lift to shelf"]["peak_pressure_kPa"]),
    "tauFast": fmt(t["Fast curl"]["elbow_torque_Nm"], 2), "tauHold": fmt(t["Static hold"]["elbow_torque_Nm"], 2),
    "collapseA": fmt(d["collapse_intercept"], 2), "collapseB": fmt(d["collapse_slope"], 2),
    "collapseR": fmt(d["collapse_r2"], 3), "engagedMM": fmt(d["engaged_length_mm"], 0),
    "gripMM": fmt(d["grip_distance_mm"], 0), "radiusMM": fmt(d["radius_mm"]),
    "lifeCyl": fmt(w["cylindrical"]["lifetime_months"]), "lifeTap": fmt(w["tapered"]["lifetime_months"]),
    "liftShare": fmt(100 * w["cylindrical"]["lift_share_at_fit"], 0),
    "fitShareFail": fmt(100 * w["cylindrical"]["fit_share_at_failure"], 0),
    "rideUpFail": fmt(w["tapered_ride_up_at_failure_mm"]), "engagedFail": fmt(w["tapered_engaged_at_failure_mm"], 0),
    "socketsStdBoy": str(r["boy_standard"]["count"]), "socketsGrowthBoy": str(r["boy_growth"]["count"]),
    "socketsStdGirl": str(r["girl_standard"]["count"]), "socketsGrowthGirl": str(r["girl_growth"]["count"]),
    "closureBoy": fmt(c["boy_50th"]), "closureGirl": fmt(c["girl_50th"]),
    "closureBoyNinety": fmt(c["boy_90th"]), "closureGirlNinety": fmt(c["girl_90th"]),
    "closureBoyTen": fmt(c["boy_10th"]), "closureGirlTen": fmt(c["girl_10th"]),
    "closureTapBoy": fmt(c["boy_tapered"]), "closureTapGirl": fmt(c["girl_tapered"]),
    "mcN": str(u["samples"]), "mcStdMed": fmt(u["standard"]["median"]), "mcIndMed": fmt(u["individual"]["median"]),
    "mcIndLo": fmt(u["individual"]["lo"]), "mcIndHi": fmt(u["individual"]["hi"]),
    "mcDayOne": fmt(100 * u["individual"]["day_one"], 0), "mcSlip": fmt(100 * u["standard"]["slip_day_one"], 0),
    "mcRho": fmt(u["rho_s0_lifetime"], 2), "mcCloMed": fmt(u["closure"]["median"]),
    "mcNever": fmt(100 * u["closure"]["never_fraction"], 0), "oatBase": fmt(u["baseline_months"]),
    "deficitEleven": fmt(m["by_age"]["11"]["deficit_cm"]), "leanEleven": fmt(m["by_age"]["11"]["lean_deg"]),
    "deficitTwelve": fmt(m["by_age"]["12"]["deficit_cm"]), "leanTwelve": fmt(m["by_age"]["12"]["lean_deg"]),
    "lumbarTwelve": fmt(m["by_age"]["12"]["lumbar_pct"], 2),
    "deficitReplace": fmt(m["deficit_at_replacement_cm"]),
    "energyDrift": f"{v['energy_drift']:.0e}".replace("e-", r"\times10^{-") + "}",
    "neError": f"{v['newton_euler_error_Nm']:.0e}".replace("e-", r"\times10^{-") + "}",
    "replayError": fmt(v["replay_error_deg"], 3), "pistonK": fmt(v["pistoning_k_kN"]),
    "pistonFn": fmt(v["pistoning_fn_Hz"], 0), "pistonSlip": fmt(v["max_slip_mm"], 2),
    # Added later: how the dynamic-number line behaves at slow speeds, and how firm the closure age is.
    "piLowN": str(d["low_pi_points"]), "piAllN": str(d["collapse_points"]), "piLowCut": fmt(d["low_pi_cutoff"], 1),
    "piLowMin": fmt(d["low_pi_ratio_min"], 2), "piLowMax": fmt(d["low_pi_ratio_max"], 2),
    "piLineErr": fmt(d["collapse_max_line_error"], 2),
    "mcCloPinned": fmt(100 * u["closure"]["already_closed_at_4"], 0),
    "mcCloBetweenN": str(u["closure"]["closing_between_n"]), "mcCloBetweenMed": fmt(u["closure"]["closing_between_median"]),
    "mcCloBetweenLo": fmt(u["closure"]["closing_between_lo"]), "mcCloBetweenHi": fmt(u["closure"]["closing_between_hi"]),
    "mcCloNear": fmt(100 * u["closure"]["within_one_year_of_baseline"], 0),
    "mcCloBeforeTwelve": fmt(100 * u["closure"]["before_12"], 0),
    "mcCloLate": fmt(100 * u["closure"]["after_15_or_never"], 0),
    "mcCloOverall": fmt(u["closure"]["median_never_counted_as_late"]),
    "mcCloRho": fmt(u["spearman_closure"]["residual_fraction"], 2),
    "sensLoadHighBoy": fmt(k["object = 2.5% of body mass"]["boy"]), "sensLoadHighGirl": fmt(k["object = 2.5% of body mass"]["girl"]),
    "sensLoadTopBoy": fmt(k["object = 3.0% of body mass"]["boy"]), "sensLoadTopGirl": fmt(k["object = 3.0% of body mass"]["girl"]),
    "sensTolLowBoy": fmt(k["pressure tolerance 75 kPa"]["boy"]), "sensTolLowGirl": fmt(k["pressure tolerance 75 kPa"]["girl"]),
    "sensLimbEightBoy": fmt(k["limb follows the 25% growth rule from age 8"]["boy"]),
    "sensLimbEightGirl": fmt(k["limb follows the 25% growth rule from age 8"]["girl"]),
    "sensLimbSixBoy": fmt(k["limb follows the 25% growth rule from age 6"]["boy"]),
    "sensLimbSixGirl": fmt(k["limb follows the 25% growth rule from age 6"]["girl"]),
    "sensMassBoy": fmt(k["prosthesis mass grows with height"]["boy"]), "sensMassGirl": fmt(k["prosthesis mass grows with height"]["girl"]),
    "sensMassCubeBoy": fmt(k["prosthesis mass grows with height³"]["boy"]),
    "sensMassCubeGirl": fmt(k["prosthesis mass grows with height³"]["girl"]),
    # ---- added for the robustness / validation / ODE rewrite (scripts 12-16) ----
    "pZeroEight": fmt(tab["boy_cylindrical_8"]["P0_kPa"]), "headroomBase": fmt(100 * (BASE_TOL / (tab["boy_cylindrical_8"]["P0_kPa"] * 1e3) - 1), 0),
    "tPlusBoyCyl": fmt(tab["boy_cylindrical_8"]["T"]["0.25"], 0), "tPlusBoyTap": fmt(tab["boy_tapered_8"]["T"]["0.25"], 0),
    "tPlusGirlCyl": fmt(tab["girl_cylindrical_8"]["T"]["0.25"], 0), "tPlusGirlTap": fmt(tab["girl_tapered_8"]["T"]["0.25"], 0),
    "tPlusMin": fmt(min(tplus), 0), "tPlusMax": fmt(max(tplus), 0),
    "tTenBoyCyl": fmt(tab["boy_cylindrical_8"]["T"]["0.1"], 0), "tFiftyBoyCyl": fmt(tab["boy_cylindrical_8"]["T"]["0.5"], 0),
    "impliedCyl": fmt(hd["implied"]["cylindrical"]["at_mean_kPa"], 0), "impliedTap": fmt(hd["implied"]["tapered"]["at_mean_kPa"], 0),
    "headroomGap": fmt(hd["worst_gap_months"], 2),
    "cloMcN": str(cp["n"]), "cloAnever": fmt(100 * A["never"], 0), "cloBnever": fmt(100 * B["never"], 0),
    "cloAclosed": fmt(100 * (1 - A["never"]), 0), "cloBclosed": fmt(100 * (1 - B["never"]), 0),
    "cloAbyTwelve": fmt(100 * A["p_by_12"], 0), "cloBbyTwelve": fmt(100 * B["p_by_12"], 0),
    "cloAbyFourteen": fmt(100 * A["p_by_14"], 0), "cloBbyFourteen": fmt(100 * B["p_by_14"], 0),
    "cloAmed": fmt(A["median_all"]), "cloBmed": fmt(B["median_all"]), "cloAtFour": fmt(100 * A["closed_at_4"], 0),
    "cloAfLow": fmt(100 * A["p_close_given_f"][0], 0), "cloAfHigh": fmt(100 * A["p_close_given_f"][3], 0),
    "cloBfLow": fmt(100 * B["p_close_given_f"][0], 0), "cloBfHigh": fmt(100 * B["p_close_given_f"][3], 0),
    "cloAfMid": fmt(100 * A["p_close_given_f"][1], 0), "cloBfMid": fmt(100 * B["p_close_given_f"][1], 0),
    "odeGap": fmt(ode["worst_gap_months"], 3), "odeN": str(ode["n_lifetimes"]), "odeSusp": str(ode["n_suspension"]),
    "odeStateErr": sci(max(ode["state_errors"].values())), "odeConserved": sci(ode["conserved_drift"]),
    "budgetLo": fmt(ode["budget_day_one_pct"]), "budgetHi": fmt(ode["budget_end_pct"]), "girthRate": fmt(ode["girth_rate_pct_per_year"]),
    "bracketLo": fmt(ode["bracket_months"][0]), "bracketHi": fmt(ode["bracket_months"][1]), "timeRatio": sci(ode["time_scale_ratio"]),
    "eventMonths": fmt(ode["event_months"], 2),
    "mcMedStd": fmt(va["mc_median_standard"]), "mcWithinObs": fmt(100 * va["mc_share_within_observed_1sd"], 0),
    "mcInRec": fmt(100 * va["mc_share_in_recommended"], 0), "mcDayOneStd": fmt(100 * va["mc_share_day_one_failure"], 0),
    "mcLastMean": fmt(va["mc_mean_among_those_that_last"]), "mcLastSd": fmt(va["mc_sd_among_those_that_last"]),
    "pptMean": fmt(vb["ppt_mean"], 0), "pptSd": fmt(vb["ppt_sd"], 0), "tolPct": fmt(vb["tolerance_percentile"], 0),
    "impPctCyl": fmt(vb["implied_percentile"]["cylindrical"], 0), "impPctTap": fmt(vb["implied_percentile"]["tapered"], 0),
    "mcTolLoPct": fmt(vb["mc_range_percentile"][0], 0), "mcTolHiPct": fmt(vb["mc_range_percentile"][1], 0),
    "dayOnePPT": fmt(100 * vb["day_one_peak_over_ppt"], 0),
    "girthBoyModel": fmt(vc["boy"]["model_pct"], 0), "girthBoyMuac": fmt(vc["boy"]["muac_pct"], 0), "girthBoyWrist": fmt(vc["boy"]["wrist_pct"], 0),
    "girthGirlModel": fmt(vc["girl"]["model_pct"], 0), "girthGirlMuac": fmt(vc["girl"]["muac_pct"], 0), "girthGirlWrist": fmt(vc["girl"]["wrist_pct"], 0),
    "volSix": fmt(val["E_volume"]["age_6.0"], 0), "volTwelve": fmt(val["E_volume"]["age_12.0"], 0),
    "phiLifeLow": fmt(vd["0.10"]["lifetime_boy_cyl_8"]), "phiLifeMid": fmt(vd["0.20"]["lifetime_boy_cyl_8"]),
    "phiCloLow": fmt(vd["0.10"]["closure_boy_rule_B"]), "phiCloMid": fmt(vd["0.20"]["closure_boy_rule_B"]),
    "oosMin": fmt(min(oos)), "oosMax": fmt(max(oos)),
    "kappaQuarterBoy": fmt(ha["boy"][ha["kappa"].index(0.25)]), "kappaZeroBoy": fmt(ha["boy"][0]),
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(f"\\newcommand{{\\{k}}}{{{val}}}" for k, val in macros.items()) + "\n")
print(f"  paper/generated/numbers.tex ({len(macros)} values)")
