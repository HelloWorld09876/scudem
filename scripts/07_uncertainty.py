import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

from common import BASE, BOY, FIT_AGE, GROWING
from pedsocket.lifetime import window_closure_age
from pedsocket.lifetime import socket_lifetime
from pedsocket.config import RESULT_DIR
from pedsocket.plotting import record, save
from pedsocket.uncertainty import run_monte_carlo

LABELS = {
    "tissue_modulus": "tissue modulus E", "tissue_stiffening": "tissue stiffening B",
    "pressure_tolerance": "pressure tolerance", "friction": "skin–socket friction",
    "prosthesis_mass": "prosthesis mass", "object_mass": "object mass", "residual_fraction": "residual-limb length",
    "soft_tissue_fraction": "soft-tissue thickness", "atrophy_ratio": "residual-limb radius",
    "speed_factor": "movement speed", "fit_strain": "fit tightness", "proximal_growth_share": "proximal growth share",
}

base = socket_lifetime(BOY, FIT_AGE, BASE).months
rows = []
for key, label in LABELS.items():
    lo = socket_lifetime(BOY, FIT_AGE, BASE.scaled(key, 0.75)).months - base
    hi = socket_lifetime(BOY, FIT_AGE, BASE.scaled(key, 1.25)).months - base
    rows.append((label, lo, hi))
rows.sort(key=lambda r: max(abs(r[1]), abs(r[2])))
fig, ax = plt.subplots(figsize=(9, 5.6))
y = np.arange(len(rows))
ax.barh(y, [r[1] for r in rows], color="#93c5fd", label="parameter −25%")
ax.barh(y, [r[2] for r in rows], color="#fdba74", label="parameter +25%")
ax.axvline(0, color="k", lw=1)
ax.axvline(-base, color="#dc2626", ls=":", lw=1.2)
ax.text(-base + 0.3, len(rows) - 0.6, "fails on\nday one", color="#dc2626", fontsize=8.5, va="top")
ax.set_yticks(y, [r[0] for r in rows])
ax.set(xlabel=f"change in socket lifetime (months), baseline {base:.1f} months",
       title="One-at-a-time sensitivity, boy fitted at 8")
ax.legend(fontsize=9, loc="lower right")
save(fig, "fig10_tornado")
for label, lo, hi in rows[::-1]:
    print(f"  {label:24s} −25%: {lo:+6.1f}   +25%: {hi:+6.1f}")

mc = run_monte_carlo(BASE, GROWING, n=400)
clo_headline = window_closure_age(BOY, GROWING)  # the baseline closure age for a median boy, for comparison
std_med, std_lo, std_hi = mc.interval(mc.lifetime_standard)
ind_med, ind_lo, ind_hi = mc.interval(mc.lifetime_individual)
clo_med, clo_lo, clo_hi = mc.interval(mc.closure_age)
slip_std = float(np.mean(mc.slips_standard & (mc.lifetime_standard == 0)))
day_one_ind = float(np.mean(mc.lifetime_individual == 0))
never = float(np.mean(~np.isfinite(mc.closure_age)))
# The closure summary above only counts samples that close somewhere between 4 and 18. Break the rest out so the headline
# number is not read as "what usually happens": some samples are already closed at the first age we test (4 y), and a third
# never close.
pinned = float(np.mean(mc.closure_age == 4.0))
between = mc.closure_age[np.isfinite(mc.closure_age) & (mc.closure_age > 4.0)]
btw_med, btw_lo, btw_hi = (float(v) for v in (np.median(between), *np.quantile(between, [0.05, 0.95])))
near_headline = float(np.mean(np.abs(mc.closure_age - clo_headline) <= 1.0))
before_12 = float(np.mean(mc.closure_age < 12.0))
late_or_never = float(np.mean((mc.closure_age > 15.0) | ~np.isfinite(mc.closure_age)))
median_never_as_late = float(np.median(np.where(np.isfinite(mc.closure_age), mc.closure_age, np.inf)))
viable = mc.lifetime_individual > 0
rho_s0 = float(spearmanr(mc.initial_index[viable], mc.lifetime_individual[viable]).statistic)
rho_life = mc.rank_correlations(np.where(viable, mc.lifetime_individual, np.nan))
rho_clo = mc.rank_correlations(mc.closure_age)

fig, ax = plt.subplots(2, 2, figsize=(15, 10))
bins = np.linspace(0, 60, 31)
ax[0, 0].hist(mc.lifetime_standard, bins=bins, color="#9ca3af", alpha=0.8, label="standard 5% fit")
ax[0, 0].hist(mc.lifetime_individual, bins=bins, color="#1f5fa8", alpha=0.6, label="patient-specific fit")
ax[0, 0].set(xlabel="socket lifetime (months)", ylabel="samples",
             title=f"Patient-specific fit: median {std_med:.1f} → {ind_med:.1f} months; "
                   f"{100 * day_one_ind:.0f}% unsafe from day one")
ax[0, 0].legend(fontsize=9)
sc = ax[0, 1].scatter(mc.initial_index[viable], mc.lifetime_individual[viable], s=10, c="#c2410c", alpha=0.6)
ax[0, 1].set(xlabel=r"stress index on the day of fitting  $S_0 = p_{peak}/p_{tol}$", ylabel="lifetime (months)",
             title=f"$S_0$ predicts how long the socket lasts (Spearman ρ = {rho_s0:.2f})")
finite = mc.closure_age[np.isfinite(mc.closure_age)]
ax[1, 0].hist(finite, bins=np.arange(4, 18.5, 0.5), color="#c2410c", alpha=0.8)
ax[1, 0].axvline(clo_headline, color="k", lw=1.5, label=f"baseline run {clo_headline:.1f} y")
ax[1, 0].set(xlabel="window-closure age (years)", ylabel="samples",
             title=f"Closure age: {100 * pinned:.0f}% already closed at 4, {100 * never:.0f}% never close by 18")
ax[1, 0].legend(fontsize=9)
order = sorted(mc.names, key=lambda n: abs(rho_life[n]) + abs(rho_clo[n]))
yy = np.arange(len(order))
ax[1, 1].barh(yy - 0.2, [rho_life[n] for n in order], 0.4, color="#1f5fa8", label="lifetime")
ax[1, 1].barh(yy + 0.2, [rho_clo[n] for n in order], 0.4, color="#c2410c", label="closure age")
ax[1, 1].set_yticks(yy, [LABELS[n] for n in order])
ax[1, 1].axvline(0, color="k", lw=1)
ax[1, 1].set(xlabel="Spearman rank correlation", title=f"Global sensitivity ({len(mc.lifetime_standard)} Latin-hypercube samples)")
ax[1, 1].legend(fontsize=9)
save(fig, "fig11_monte_carlo")
# Keep the raw samples so that scripts/16_validation.py can compare them with clinical data without re-running the study.
np.savez(RESULT_DIR / "07_mc_samples.npz", names=np.array(mc.names), samples=mc.samples, initial_index=mc.initial_index,
         lifetime_standard=mc.lifetime_standard, lifetime_individual=mc.lifetime_individual, closure_age=mc.closure_age)
print(f"  standard fit: median {std_med:.1f} mo, day-one failure {100 * np.mean(mc.lifetime_standard == 0):.1f}% "
      f"(slipping {100 * slip_std:.1f}%)")
print(f"  patient-specific fit: median {ind_med:.1f} mo (90%: {ind_lo:.1f}–{ind_hi:.1f}), day-one failure {100 * day_one_ind:.1f}%")
print(f"  closure: {100 * pinned:.1f}% already closed at 4 y, {100 * never:.1f}% never by 18; of the {len(between)} that close in between: "
      f"median {btw_med:.1f} y (90%: {btw_lo:.1f}–{btw_hi:.1f}); {100 * near_headline:.1f}% within a year of the baseline {clo_headline:.1f} y; "
      f"{100 * before_12:.1f}% before 12 y; {100 * late_or_never:.1f}% after 15 y or never")
print(f"  S0 vs lifetime Spearman {rho_s0:.2f}; closure median {clo_med:.2f} y (90%: {clo_lo:.2f}–{clo_hi:.2f}), never {100 * never:.1f}%")
top = sorted(rho_life, key=lambda n: -abs(rho_life[n]))[:3]
print("  strongest drivers of lifetime: " + ", ".join(f"{LABELS[n]} ({rho_life[n]:+.2f})" for n in top))
record("07_uncertainty", dict(oat=[dict(parameter=r[0], minus25=r[1], plus25=r[2]) for r in rows], baseline_months=base,
                              standard=dict(median=std_med, lo=std_lo, hi=std_hi, slip_day_one=slip_std,
                                            day_one=float(np.mean(mc.lifetime_standard == 0))),
                              individual=dict(median=ind_med, lo=ind_lo, hi=ind_hi, day_one=day_one_ind),
                              closure=dict(median=clo_med, lo=clo_lo, hi=clo_hi, never_fraction=never,
                                           already_closed_at_4=pinned, closing_between_median=btw_med,
                                           closing_between_lo=btw_lo, closing_between_hi=btw_hi,
                                           closing_between_n=int(len(between)), within_one_year_of_baseline=near_headline,
                                           before_12=before_12, after_15_or_never=late_or_never,
                                           median_never_counted_as_late=median_never_as_late),
                              rho_s0_lifetime=rho_s0, spearman_lifetime=rho_life, spearman_closure=rho_clo,
                              top_drivers=[LABELS[n] for n in top], samples=len(mc.lifetime_standard)))
