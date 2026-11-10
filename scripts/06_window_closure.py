import numpy as np
import matplotlib.pyplot as plt

from common import CENTILES, GROWING, TAPERED
from pedsocket import Child
from pedsocket.lifetime import fresh_socket_margin, window_closure_age
from pedsocket.plotting import LIMIT, record, save, sex_color

ages = np.arange(5.0, 18.01, 0.25)
summary = {}
fig, ax = plt.subplots(1, 2, figsize=(14, 4.6))
for sex in ("boy", "girl"):
    for name, z in CENTILES.items():
        child = Child(sex, z)
        closure = window_closure_age(child, GROWING)
        summary[f"{sex}_{name}"] = closure if np.isfinite(closure) else None
        if name == "50th":
            margin = np.array([fresh_socket_margin(child, a, GROWING) for a in ages])
            ax[0].plot(ages, 100 * margin, color=sex_color(sex), lw=2.4, label=f"{sex}, 50th centile")
            ax[0].axvline(closure, color=sex_color(sex), ls=":", lw=1.4)
            # Labels sit above the curves, on either side of their own line, so they never cover the data.
            side = -0.15 if sex == "boy" else 0.15
            ax[0].text(closure + side, 27, f"{sex}: closes at {closure:.1f} y", color=sex_color(sex), fontsize=9,
                       ha="right" if sex == "boy" else "left")
        print(f"  {sex:4s} {name:4s}: window closes at {closure:.2f} y")
    tapered_closure = window_closure_age(Child(sex), TAPERED.updated(load_mode="scaled"))
    summary[f"{sex}_tapered"] = tapered_closure
ax[0].axhline(0, color=LIMIT, ls="--", lw=1.2)
ax[0].set(xlabel="age (years)", ylabel="pressure margin of a brand-new socket (%)",
          title="A brand-new socket slowly runs out of margin")
ax[0].legend(fontsize=9)
labels = list(CENTILES)
x = np.arange(len(labels))
for i, sex in enumerate(("boy", "girl")):
    values = np.array([np.nan if summary[f"{sex}_{c}"] is None else summary[f"{sex}_{c}"] for c in labels])
    shown = np.where(np.isfinite(values), values, 18.0)
    bars = ax[1].bar(x + (i - 0.5) * 0.35, shown, 0.35, color=sex_color(sex), label=sex)
    for bar, v in zip(bars, values):
        if not np.isfinite(v):
            bar.set_hatch("//")
            bar.set_alpha(0.35)
        ax[1].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                   f"{v:.1f}" if np.isfinite(v) else "open\nat 18", ha="center", fontsize=9)
ax[1].set_xticks(x, [f"{c} centile" for c in labels])
ax[1].set(ylabel="closure age (years)", ylim=(10, 19.5), title="Closure age for small, median and large children")
ax[1].legend(fontsize=9)
# This number depends on a few assumptions that are easy to argue with. Say so on the figure itself.
fig.text(0.5, -0.045, "Assumes an object of 2% of body mass, a pressure tolerance of 100 kPa, and a residual limb that is 45% of the "
                       "forearm at every fitting age. Changing any of these moves the closure age a lot (see the sensitivity figure).",
         ha="center", fontsize=8.5, color="#555")
save(fig, "fig09_window_closure")
record("06_window_closure", summary)
