"""Checks of the model against published data that the model was NOT built from.

What can and cannot be tested (honest scope):
  * No measured pressure-time histories of children's residual limbs exist in the sources we could reach, so the pressure model
    itself cannot be validated against child data. Everything below tests the pieces around it.
  * The clinical replacement interval (Ghidini et al. 2025) is for children with LOWER-limb loss in Cambodia, not transradial.
    It is used as a check on the time scale of growth-driven socket replacement, not as a calibration of an upper-limb model.
  * One number was effectively tuned: the 100 kPa tolerance. So the comparison with the replacement interval is a consistency
    check of that single parameter ("implied tolerance"), not an independent test.

Checks:
  A. model socket lifetimes vs observed replacement interval (16.4 +/- 9.9 months; recommended 12-18 months)
  B. assumed / implied pressure tolerance vs children's measured pressure-pain thresholds (Nikolajsen et al. 2011)
  C. growth-plate share: effect of the proximal growth share phi on lifetime, with Pritchett's 1991 shares
  D. girth growth 6 -> 17 y of the model vs measured arm and wrist circumferences (Turkish reference samples)
  E. residual-limb volume growth per year vs the maximum reported by Ghidini's group (conference poster)
  F. out-of-sample test of the Preece-Baines growth ODE: fit to ages up to a cut-off, predict the CDC centile afterwards
"""
import json

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import least_squares
from scipy.stats import norm

from common import BASE, BOY, CHILDREN, FIT_AGE, GIRL, GROWING
from pedsocket import body_at, design_socket
from pedsocket.config import RESULT_DIR
from pedsocket.growth import centile_curve, preece_baines
from pedsocket.lifetime import limb_grows_by_rule, socket_lifetime, window_closure_age
from pedsocket.plotting import BOY as BOY_C, GIRL as GIRL_C, LIMIT, record, save

# ---- published numbers used (see docs/Report_on_Use_of_AI.md and paper references for sources) ----------------------------
GHIDINI = dict(mean=16.4, sd=9.9, adjust_mean=8.3, adjust_sd=6.6, rec=(12.0, 18.0), rec_adjust=(3.0, 6.0), n_casefiles=62)
PPT = dict(leg=(183.1, 90.7), thenar=(179.1, 97.4), n=50, ages="4-12")                                # kPa, mean (SD)
MUAC_TURKISH = dict(boy=(17.0, 23.6), girl=(15.6, 20.9))                                              # cm, 50th centile, "ranged from .. to .."
WRIST_TURKISH = dict(boy=(13.00, 16.83), girl=(12.48, 15.58))                                         # cm, mean at 6 y and 17 y
POSTER_VOLUME_MAX_PER_YEAR = 60.0                                                                      # %/yr, "up to", below-knee casefiles
ADULT_SOCKET_KPA = (38.0, 41.0)                                                                       # air-splint transhumeral socket, adults

out = {}

# ---- A. replacement interval ----------------------------------------------------------------------------------------------
mc = np.load(RESULT_DIR / "07_mc_samples.npz")
std = mc["lifetime_standard"]
ind = mc["lifetime_individual"]
lo, hi = GHIDINI["mean"] - GHIDINI["sd"], GHIDINI["mean"] + GHIDINI["sd"]
a = dict(
    mc_median_standard=float(np.median(std)), mc_median_individual=float(np.median(ind)),
    mc_share_within_observed_1sd=float(np.mean((std >= lo) & (std <= hi))),
    mc_share_in_recommended=float(np.mean((std >= GHIDINI["rec"][0]) & (std <= GHIDINI["rec"][1]))),
    mc_share_day_one_failure=float(np.mean(std == 0)),
    mc_sd_among_those_that_last=float(np.std(std[std > 0])), mc_mean_among_those_that_last=float(np.mean(std[std > 0])),
    deterministic_boy_cyl_5_to_12=[float(socket_lifetime(BOY, x, BASE).months) for x in (5.0, 8.0, 12.0)],
    deterministic_girl_cyl_5_to_12=[float(socket_lifetime(GIRL, x, BASE).months) for x in (5.0, 8.0, 12.0)],
    deterministic_boy_tap_5_to_12=[float(socket_lifetime(BOY, x, BASE.updated(socket_shape="tapered")).months) for x in (5.0, 8.0, 12.0)],
)
head = json.loads((RESULT_DIR / "13_headroom_law.json").read_text())
a["implied_tolerance_kPa"] = {k: v["at_mean_kPa"] for k, v in head["implied"].items()}
out["A_replacement_interval"] = a
print(f"  A: model (Monte Carlo, boy fitted at 8, standard fit) median {a['mc_median_standard']:.1f} months, "
      f"{100 * a['mc_share_within_observed_1sd']:.0f}% inside the observed mean±1SD ({lo:.1f}–{hi:.1f}), "
      f"{100 * a['mc_share_in_recommended']:.0f}% inside the recommended 12–18; "
      f"mean±SD of those that last {a['mc_mean_among_those_that_last']:.1f}±{a['mc_sd_among_those_that_last']:.1f}")
print(f"     implied tolerance for the observed mean: {a['implied_tolerance_kPa']['cylindrical']:.0f} kPa (cylindrical), "
      f"{a['implied_tolerance_kPa']['tapered']:.0f} kPa (tapered)")

# ---- B. tolerance vs pressure-pain thresholds -----------------------------------------------------------------------------
m, s = PPT["leg"]
tol = BASE.pressure_tolerance / 1e3
b = dict(ppt_mean=m, ppt_sd=s, tolerance_z=(tol - m) / s, tolerance_percentile=float(100 * norm.cdf((tol - m) / s)),
         implied_percentile={k: float(100 * norm.cdf((v - m) / s)) for k, v in a["implied_tolerance_kPa"].items()},
         mc_range_percentile=[float(100 * norm.cdf((x - m) / s)) for x in (75.0, 125.0)],
         day_one_peak_over_ppt=float(head["table"]["boy_cylindrical_8"]["P0_kPa"] / m))
out["B_pain_threshold"] = b
print(f"  B: assumed 100 kPa sits at the {b['tolerance_percentile']:.0f}th percentile of children's pressure-pain thresholds "
      f"(mean {m} kPa, SD {s}); implied tolerances at the {b['implied_percentile']['cylindrical']:.0f}th / "
      f"{b['implied_percentile']['tapered']:.0f}th; day-one peak is {100 * b['day_one_peak_over_ppt']:.0f}% of the mean threshold")

# ---- C. growth-plate share ------------------------------------------------------------------------------------------------
c = {}
for phi in (0.10, 0.15, 0.20, 0.25, 0.30):
    p = BASE.updated(proximal_growth_share=phi)
    pg = GROWING.updated(proximal_growth_share=phi)
    c[f"{phi:.2f}"] = dict(lifetime_boy_cyl_8=float(socket_lifetime(BOY, FIT_AGE, p).months),
                           closure_boy_rule_B=float(window_closure_age(BOY, pg, params_at=limb_grows_by_rule(BOY, pg, 6.0))))
    print(f"  C: phi {phi:.2f}: lifetime {c[f'{phi:.2f}']['lifetime_boy_cyl_8']:.1f} mo, closure (self-consistent limb) "
          f"{c[f'{phi:.2f}']['closure_boy_rule_B']:.1f} y")
out["C_growth_share"] = c

# ---- D. girth growth, model vs data --------------------------------------------------------------------------------------
d = {}
for child in CHILDREN:
    r6, r17 = (body_at(child, a_, BASE).forearm_radius for a_ in (6.0, 17.0))
    mu, wr = MUAC_TURKISH[child.sex], WRIST_TURKISH[child.sex]
    d[child.sex] = dict(model_pct=100 * (r17 / r6 - 1), muac_pct=100 * (mu[1] / mu[0] - 1), wrist_pct=100 * (wr[1] / wr[0] - 1))
    print(f"  D: {child.sex}: girth growth 6→17 y  model +{d[child.sex]['model_pct']:.0f}%   mid-upper arm +{d[child.sex]['muac_pct']:.0f}%   "
          f"wrist +{d[child.sex]['wrist_pct']:.0f}%")
out["D_girth"] = d

# ---- E. volume growth per year ---------------------------------------------------------------------------------------------
socket = design_socket(BOY, FIT_AGE, BASE)
def residual_volume(age):
    b_ = body_at(BOY, age, BASE)
    length = socket.residual_length_at_fit + BASE.proximal_growth_share * (b_.forearm_length - socket.forearm_length_at_fit)
    return np.pi * b_.residual_radius**2 * length
e = {f"age_{x}": 100 * (residual_volume(x + 1.0) / residual_volume(x) - 1) for x in (6.0, 8.0, 10.0, 12.0)}
e["whole_socket_life_pct"] = 100 * (residual_volume(FIT_AGE + 21.6 / 12) / residual_volume(FIT_AGE) - 1)
out["E_volume"] = e
print("  E: model residual-limb volume growth per year at 6/8/10/12 y: " + " / ".join(f"{v:.0f}%" for k, v in e.items() if k.startswith("age")) +
      f"  (reported maximum, below-knee casefiles: up to {POSTER_VOLUME_MAX_PER_YEAR:.0f}%/yr)")

# ---- F. out-of-sample growth ODE --------------------------------------------------------------------------------------------
def fit_pb(ages, heights, theta_guess):
    x0 = [heights[-1] + 8.0, heights[-1] - 6.0, 0.1, 1.0, theta_guess]
    lower = [heights[-1], 80.0, 0.01, 0.2, 8.0]
    upper = [heights[-1] + 40.0, heights[-1] + 5.0, 0.6, 4.0, 17.0]
    return least_squares(lambda q: preece_baines(ages, *q) - heights, x0, bounds=(lower, upper)).x

f = {}
for child, cuts in ((BOY, (13.0, 15.0)), (GIRL, (11.5, 13.0))):
    ages, heights = centile_curve("statage", child.sex, 0.0)
    for cut in cuts:
        train = ages <= cut
        q = fit_pb(ages[train], heights[train], 13.5 if child.sex == "boy" else 11.5)
        pred = preece_baines(ages[~train], *q)
        rmse = float(np.sqrt(np.mean((pred - heights[~train]) ** 2)))
        final = float(abs(preece_baines(20.0, *q) - heights[-1]))
        f[f"{child.sex}_train_to_{cut:g}"] = dict(rmse_cm=rmse, max_cm=float(np.max(np.abs(pred - heights[~train]))), error_at_20_cm=final)
        print(f"  F: {child.sex}: fit to ages ≤ {cut:g} → predict {cut:g}–20 y: RMSE {rmse:.2f} cm, error at 20 y {final:.2f} cm")
out["F_growth_out_of_sample"] = f

# ---- Figure ------------------------------------------------------------------------------------------------------------------
fig, ax = plt.subplots(2, 2, figsize=(14.5, 9.4))
ax[0, 0].hist(std[std > 0], bins=np.arange(0, 60, 2), color="#1f5fa8", alpha=0.75, label=f"model, boy fitted at 8 ({len(std)} samples)")
ax[0, 0].axvspan(lo, hi, color="#15803d", alpha=0.16, label="observed 16.4 ± 9.9 months (Ghidini 2025, lower limb)")
ax[0, 0].axvline(GHIDINI["mean"], color="#15803d", lw=2)
ax[0, 0].axvspan(*GHIDINI["rec"], ymin=0, ymax=0.04, color="#15803d", alpha=0.9, label="12–18 months recommended")
ax[0, 0].set(xlabel="months until the socket must be replaced", ylabel="samples", title=f"A. Replacement interval: model median {a['mc_median_standard']:.1f} vs 16.4 months observed")
ax[0, 0].legend(fontsize=8.5, loc="upper right")
ax[0, 0].text(0.98, 0.58, f"{100 * a['mc_share_day_one_failure']:.0f}% of samples are already\nover tolerance on day one (not shown)",
              transform=ax[0, 0].transAxes, ha="right", fontsize=8.5, color="#555")

x = np.linspace(0, 450, 400)
ax[0, 1].fill_between(x, norm.pdf(x, *PPT["leg"]) * 1e3, color="#9ca3af", alpha=0.5, label="children's pressure-pain thresholds\n(leg, n = 50, ages 4–12; Nikolajsen 2011)")
ax[0, 1].axvline(tol, color=LIMIT, lw=2, label="assumed tolerance 100 kPa")
for shape, colr in (("cylindrical", "#1f5fa8"), ("tapered", "#7c3aed")):
    ax[0, 1].axvline(a["implied_tolerance_kPa"][shape], color=colr, ls="--", lw=1.6, label=f"implied by 16.4-month mean, {shape}")
ax[0, 1].axvline(head["table"]["boy_cylindrical_8"]["P0_kPa"], color="#c2410c", ls=":", lw=1.8, label="model peak on day one (77 kPa)")
ax[0, 1].set(xlabel="pressure (kPa)", ylabel="relative frequency (×10⁻³)", yticks=[], title="B. The tolerance sits low in the measured threshold range")
ax[0, 1].legend(fontsize=8, loc="upper right")

x = np.arange(2)
w = 0.25
for j, (key, lab, col) in enumerate((("model_pct", "model: $r\\propto\\sqrt{M/H}$", "#c2410c"), ("muac_pct", "measured mid-upper arm", "#1f5fa8"),
                                       ("wrist_pct", "measured wrist", "#6b7280"))):
    vals = [d["boy"][key], d["girl"][key]]
    bars = ax[1, 0].bar(x + (j - 1) * w, vals, w, color=col, label=lab)
    for bar, v in zip(bars, vals):
        ax[1, 0].text(bar.get_x() + bar.get_width() / 2, v + 0.8, f"+{v:.0f}%", ha="center", fontsize=9)
ax[1, 0].set_xticks(x, ["boys", "girls"])
ax[1, 0].set(ylabel="growth in girth from 6 to 17 years (%)", ylim=(0, 56),
             title="C. Girth growth 6→17 y: model sits a little above the data")
ax[1, 0].legend(fontsize=8.5, loc="upper right")

phis = np.array(sorted(float(k) for k in c))
axr = ax[1, 1].twinx()
ax[1, 1].plot(phis, [c[f"{v:.2f}"]["lifetime_boy_cyl_8"] for v in phis], "-o", color="#1f5fa8", lw=2.2, label="socket lifetime (left)")
axr.plot(phis, [c[f"{v:.2f}"]["closure_boy_rule_B"] for v in phis], "-s", color="#c2410c", lw=2.2, label="closure age, self-consistent limb (right)")
ax[1, 1].axvspan(0.05, 0.20, color="#15803d", alpha=0.15)
ax[1, 1].text(0.125, 18.35, "proximal share of forearm growth\nfrom Pritchett 1991: about 5–20%", ha="center", fontsize=8.5, color="#15803d")
ax[1, 1].axvline(0.25, color="#374151", ls=":", lw=1.4)
ax[1, 1].text(0.2535, 22.6, "model\nbaseline", fontsize=8.5, color="#374151")
ax[1, 1].set(xlabel="proximal growth share φ of forearm growth", ylabel="lifetime of a socket fitted at 8 (months)", ylim=(18, 23.5),
             title="D. Growth-plate share: literature values move the answer modestly")
axr.set(ylabel="closure age (years)", ylim=(8.5, 12.5))
axr.spines["right"].set_visible(True)
h1, l1 = ax[1, 1].get_legend_handles_labels()
h2, l2 = axr.get_legend_handles_labels()
ax[1, 1].legend(h1 + h2, l1 + l2, fontsize=8.5, loc="lower right")
save(fig, "fig19_validation")
record("16_validation", out)
