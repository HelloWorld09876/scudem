import numpy as np
import matplotlib.pyplot as plt

from common import BASE, BOY, CHILDREN, FIT_AGE, TAPERED
from pedsocket import design_socket
from pedsocket.interface import worst_case
from pedsocket.lifetime import socket_lifetime
from pedsocket.plotting import GROWTH, LIFT, LIMIT, record, save, sex_color

summary = {}
fig, ax = plt.subplots(1, 3, figsize=(16, 4.5))
for k, (p, shape) in enumerate([(BASE, "cylindrical"), (TAPERED, "tapered")]):
    socket = design_socket(BOY, FIT_AGE, p)
    life = socket_lifetime(BOY, FIT_AGE, p)
    ages = np.linspace(FIT_AGE, FIT_AGE + 2.5, 61)
    W = [worst_case(BOY, socket, a, p) for a in ages]
    fit = np.array([w.state.fit_pressure for w in W]) / 1e3
    lift = np.array([w.peak_pressure for w in W]) / 1e3 - fit
    ax[k].stackplot(ages, lift, fit, colors=[LIFT, GROWTH], alpha=0.9,
                    labels=["lifting (socket moment)", "growth (tissue compression)"])
    ax[k].plot(ages, lift + fit, "k", lw=2, label="total peak")
    ax[k].axhline(p.pressure_tolerance / 1e3, color=LIMIT, ls="--", lw=1.2)
    ax[k].axvline(FIT_AGE + life.years, color=LIMIT, lw=1.2)
    ax[k].text(FIT_AGE + life.years + 0.04, 12, f"replace after\n{life.months:.1f} months", color=LIMIT, fontsize=9)
    ax[k].set(xlabel="age (years)", ylabel="kPa", ylim=(0, 150), title=f"{shape.capitalize()} socket fitted at {FIT_AGE:g}")
    ax[k].legend(fontsize=8.5, loc="upper left")
    if shape == "tapered":
        ax[2].plot(ages, [1000 * w.state.ride_up for w in W], color="#7c3aed", lw=2.2, label="ride-up of limb (mm)")
        ax[2].plot(ages, [1000 * w.state.engaged_length for w in W], color="#15803d", lw=2.2, label="engaged length (mm)")
        ax[2].plot(ages, [w.state.fit_pressure / 1e3 for w in W], color="#c2410c", lw=2.2, label="fit pressure (kPa)")
        ax[2].axvline(FIT_AGE + life.years, color=LIMIT, lw=1.2)
        ax[2].set(xlabel="age (years)", title="Tapered socket: limb is pushed out")
        ax[2].legend(fontsize=8.5)
        summary["tapered_ride_up_at_failure_mm"] = 1000 * life.at_failure.state.ride_up
        summary["tapered_engaged_at_failure_mm"] = 1000 * life.at_failure.state.engaged_length
    summary[shape] = dict(lifetime_months=life.months, cause=life.cause, failing_task=life.at_failure.critical_task,
                          lift_share_at_fit=float(lift[0] / (lift[0] + fit[0])),
                          fit_share_at_failure=float(life.at_failure.state.fit_pressure / life.at_failure.peak_pressure))
    print(f"  {shape:11s}: lasts {life.months:.1f} months, cause {life.cause}, task {life.at_failure.critical_task}")
save(fig, "fig06_single_socket")

fit_ages = np.arange(5.0, 16.01, 0.5)
fig, ax = plt.subplots(figsize=(8, 4.8))
table = {}
for child in CHILDREN:
    for p, ls, shape in [(BASE, "-", "cylindrical"), (TAPERED, "--", "tapered")]:
        months = np.array([socket_lifetime(child, a, p).months for a in fit_ages])
        ax.plot(fit_ages, months, ls, marker="o", ms=3, color=sex_color(child.sex), lw=2, label=f"{child.sex}, {shape}")
        table[f"{child.sex}_{shape}"] = months.tolist()
        band = months[(fit_ages >= 5) & (fit_ages <= 12)]
        print(f"  {child.sex:4s} {shape:11s}: fitted 5–12 y → {np.nanmin(band):.1f}–{np.nanmax(band):.1f} months")
ax.axhspan(12, 18, color="#e5e7eb", alpha=0.6, zorder=0, label="12–18 months, often quoted in practice")
ax.set(xlabel="age at fitting (years)", ylabel="socket lifetime (months)", ylim=(0, 60),
       title="How long a socket lasts, by age at fitting")
ax.text(8.6, 52, "curves end where the socket\noutlasts the remaining growth", fontsize=8, color="#555")
ax.legend(fontsize=8.5, loc="upper left")
save(fig, "fig07_lifetime_map")
summary["fit_ages"] = fit_ages.tolist()
summary["lifetime_months"] = table
record("04_socket_over_growth", summary)
