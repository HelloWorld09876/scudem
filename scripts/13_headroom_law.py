"""Tolerance-free version of the socket-lifetime result.

The original headline ("a socket fitted at 8 lasts 21.6 months") depends on a pressure tolerance that nobody has measured on
children's residual limbs. The *shape* of the pressure history does not. So here we compute the peak-pressure path P(t) of a
frozen socket once, and read the lifetime for any tolerance off it:

    lifetime(p_tol) = first time P(t) reaches p_tol  =  T(x),   x = p_tol / P(0) - 1   (the "pressure headroom").

Checks run here:
  * T(x) reproduces socket_lifetime() for several tolerances (same answer, found two different ways);
  * the tolerance that would make the model lifetime equal the clinical mean (Ghidini et al. 2025) is reported as an
    "implied tolerance" and compared with children's pressure-pain thresholds (Nikolajsen et al. 2011).
"""
import numpy as np
import matplotlib.pyplot as plt

from common import BASE, BOY, CHILDREN, FIT_AGE, TAPERED
from pedsocket import design_socket
from pedsocket.interface import worst_case
from pedsocket.lifetime import socket_lifetime
from pedsocket.plotting import LIMIT, record, save, sex_color

DT = 1.0 / 24.0          # half-month steps
HORIZON = 6.0            # years after fitting
GHIDINI_MEAN, GHIDINI_SD = 16.4, 9.9      # months between growth replacements (Ghidini et al. 2025, lower limb)
GHIDINI_REC = (12.0, 18.0)                # recommended replacement interval quoted in that paper


def pressure_path(child, fit_age, p, strain=None):
    socket = design_socket(child, fit_age, p, strain)
    ages = np.arange(fit_age, min(fit_age + HORIZON, 20.0) + 1e-9, DT)
    peak = np.array([worst_case(child, socket, a, p).peak_pressure for a in ages])
    return 12.0 * (ages - fit_age), peak          # months since fitting, Pa


def time_to_headroom(months, peak, x):
    """First time (months) at which the peak pressure has risen by a factor 1+x; NaN if it never does within the horizon."""
    target = (1.0 + x) * peak[0]
    above = np.nonzero(peak >= target)[0]
    if len(above) == 0:
        return np.nan
    i = above[0]
    if i == 0:
        return 0.0
    return float(np.interp(target, [peak[i - 1], peak[i]], [months[i - 1], months[i]]))


def pressure_at(months, peak, t):
    return float(np.interp(t, months, peak))


XS = (0.10, 0.25, 0.50, 1.00)
paths, table = {}, {}
for child in CHILDREN:
    for shape, p in (("cylindrical", BASE), ("tapered", TAPERED)):
        for age in (6.0, 8.0, 10.0, 12.0):
            m, P = pressure_path(child, age, p)
            paths[(child.sex, shape, age)] = (m, P)
            table[f"{child.sex}_{shape}_{age:g}"] = dict(
                P0_kPa=P[0] / 1e3, T={f"{x:g}": time_to_headroom(m, P, x) for x in XS},
                monthly_log_rate_first6=float(np.log(P[int(6 / (12 * DT))] / P[0]) / 0.5))   # per year
            print(f"  {child.sex:4s} {shape:11s} fit {age:4.1f}: P0 {P[0] / 1e3:5.1f} kPa, months to +10/25/50/100%: "
                  + "  ".join(f"{time_to_headroom(m, P, x):5.1f}" for x in XS))

# --- Check 1: reading lifetime off the path agrees with the original search-and-bisect lifetime -----------------------
check_rows, worst_gap = [], 0.0
m8, P8 = paths[("boy", "cylindrical", 8.0)]
for tol_kpa in (80.0, 90.0, 100.0, 120.0, 150.0):
    direct = socket_lifetime(BOY, FIT_AGE, BASE.updated(pressure_tolerance=tol_kpa * 1e3))
    x = tol_kpa * 1e3 / P8[0] - 1.0
    via_path = time_to_headroom(m8, P8, x)
    gap = abs(via_path - direct.months)
    worst_gap = max(worst_gap, gap)
    check_rows.append(dict(tolerance_kPa=tol_kpa, headroom=x, lifetime_direct=direct.months, lifetime_from_path=via_path, cause=direct.cause))
    print(f"  tol {tol_kpa:5.0f} kPa: headroom {100 * x:5.1f}%  search {direct.months:5.2f} mo  from path {via_path:5.2f} mo  ({direct.cause})")
print(f"  largest disagreement {worst_gap:.2f} months (path step is {12 * DT:.1f} months)")

# --- Implied tolerance: what would the tolerance have to be to reproduce the clinical mean? -------------------------------
implied = {}
for shape in ("cylindrical", "tapered"):
    m, P = paths[("boy", shape, 8.0)]
    implied[shape] = dict(
        at_mean_kPa=pressure_at(m, P, GHIDINI_MEAN) / 1e3,
        at_12_kPa=pressure_at(m, P, GHIDINI_REC[0]) / 1e3, at_18_kPa=pressure_at(m, P, GHIDINI_REC[1]) / 1e3,
        rise_at_mean_pct=100 * (pressure_at(m, P, GHIDINI_MEAN) / P[0] - 1.0), P0_kPa=P[0] / 1e3)
    print(f"  {shape:11s}: peak pressure 12 / 16.4 / 18 months after fitting = "
          f"{implied[shape]['at_12_kPa']:.0f} / {implied[shape]['at_mean_kPa']:.0f} / {implied[shape]['at_18_kPa']:.0f} kPa "
          f"(day one {P[0] / 1e3:.0f} kPa)")

# --- Figure ----------------------------------------------------------------------------------------------------------------
fig, ax = plt.subplots(1, 3, figsize=(17, 4.9))
for (sex, shape, age), (m, P) in paths.items():
    if age != 8.0:
        continue
    ax[0].plot(m, P / 1e3, color=sex_color(sex), ls="-" if shape == "cylindrical" else "--", lw=2.2, label=f"{sex}, {shape}")
ax[0].axhline(BASE.pressure_tolerance / 1e3, color=LIMIT, ls=":", lw=1.4)
ax[0].text(1, BASE.pressure_tolerance / 1e3 + 1.5, "baseline tolerance 100 kPa (assumed)", color=LIMIT, fontsize=8.5)
ax[0].axvspan(*GHIDINI_REC, color="#e5e7eb", alpha=0.7, zorder=0)
ax[0].text(18.4, 24, "12–18 mo\nrecommended\nreplacement", fontsize=8, color="#555", ha="right", va="bottom")
ax[0].set(xlim=(0, 30), ylim=(20, 135), xlabel="months since fitting (fitted at age 8)", ylabel="peak interface pressure (kPa)",
          title="The pressure path does not depend on the tolerance")
ax[0].legend(fontsize=8.5, loc="upper left")
tols = np.linspace(60, 160, 41)
for shape, p, ls in (("cylindrical", BASE, "-"), ("tapered", TAPERED, "--")):
    m, P = paths[("boy", shape, 8.0)]
    ax[1].plot(tols, [time_to_headroom(m, P, t * 1e3 / P[0] - 1.0) for t in tols], ls, color=sex_color("boy"), lw=2.2, label=f"boy, {shape}")
ax[1].axhspan(*GHIDINI_REC, color="#e5e7eb", alpha=0.7, zorder=0, label="12–18 months (recommended)")
ax[1].axhline(GHIDINI_MEAN, color="#15803d", lw=1.4)
ax[1].text(105, 5, "green line: observed mean 16.4 ± 9.9 mo\n(lower limb, Cambodia)", color="#15803d", fontsize=8.5)
ax[1].axvline(100, color=LIMIT, ls=":", lw=1.2)
ax[1].set(xlabel="assumed pressure tolerance (kPa)", ylabel="socket lifetime (months)", ylim=(0, 45),
          title="Lifetime is a curve in the tolerance, not a number")
ax[1].legend(fontsize=8.5, loc="upper left")
ages = (6.0, 8.0, 10.0, 12.0)
for sex in ("boy", "girl"):
    for shape, ls in (("cylindrical", "-"), ("tapered", "--")):
        ax[2].plot(ages, [time_to_headroom(*paths[(sex, shape, a)], 0.25) for a in ages], ls, marker="o", ms=4,
                   color=sex_color(sex), lw=2, label=f"{sex}, {shape}")
ax[2].axhspan(*GHIDINI_REC, color="#e5e7eb", alpha=0.7, zorder=0)
ax[2].set(xlabel="age at fitting (years)", ylabel="months until peak pressure is 25% higher", ylim=(0, 40),
          title="Tolerance-free interval: time to +25% pressure")
ax[2].legend(fontsize=8.5, loc="upper right", ncol=2)
save(fig, "fig16_headroom_law")

record("13_headroom_law", dict(
    table=table, check=check_rows, worst_gap_months=worst_gap, implied=implied,
    ghidini=dict(mean=GHIDINI_MEAN, sd=GHIDINI_SD, recommended=list(GHIDINI_REC)),
    headroom_values=list(XS)))
