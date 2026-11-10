"""Extra sensitivity for the window-closure age (review addition, not part of the original pipeline).

Two questions the closure analysis in script 11 did not ask:
  1. The fast curl lasts 0.5 s at EVERY age. What if movement time grows with body size, T(a) = 0.5 s * (H(a)/H(10))**kappa?
     kappa = 0 is the baseline; kappa = 0.5 is dynamic (Froude) similarity, i.e. the same relative speed at every age.
  2. Object share of body mass and pressure tolerance were varied one at a time. Mapped together, do they act as one knob?

Run from the repo root:  python scripts/12_closure_hidden_assumptions.py      (about 40 s)
Writes figures/fig15_closure_hidden_assumptions.png and results/12_closure_hidden_assumptions.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pedsocket import Child, body_at, load_params          # noqa: E402
from pedsocket.lifetime import window_closure_age           # noqa: E402

P = load_params()
GROWING = P.updated(load_mode="scaled")
BOY, GIRL = Child("boy"), Child("girl")
BLUE, ORANGE, INK, MUTE = "#1f5fa8", "#c2410c", "#1f2937", "#6b7280"


def closure_with_duration_exponent(child, kappa, ref_age=10.0):
    h0 = body_at(child, ref_age, GROWING).height
    at = lambda a: GROWING.updated(speed_factor=float((body_at(child, a, GROWING).height / h0) ** (-kappa)))
    return window_closure_age(child, GROWING, params_at=at)


kappas = np.array([0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.35, 0.5])
boy = np.array([closure_with_duration_exponent(BOY, k) for k in kappas])
girl = np.array([closure_with_duration_exponent(GIRL, k) for k in kappas])
print("kappa   boy      girl")
for k, b, g in zip(kappas, boy, girl):
    print(f"{k:5.2f}  {'none<18' if np.isnan(b) else f'{b:6.2f}'}  {'none<18' if np.isnan(g) else f'{g:6.2f}'}")

shares = np.arange(1.0, 3.51, 0.25)          # object, % of body mass
tols = np.arange(60, 201, 10)                # kPa
grid = np.array([[window_closure_age(BOY, GROWING.updated(object_fraction=float(f) / 100, pressure_tolerance=float(t) * 1e3))
                  for f in shares] for t in tols])

plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#9ca3af",
                     "axes.labelcolor": INK, "text.color": INK, "xtick.color": MUTE, "ytick.color": MUTE})
fig, ax = plt.subplots(1, 2, figsize=(14, 5.4), gridspec_kw={"width_ratios": [1, 1.15]}, layout="none")
a = ax[0]
for y, c, name, off in ((boy, BLUE, "boy", -0.006), (girl, ORANGE, "girl", 0.006)):
    ok = np.isfinite(y)
    a.plot(kappas[ok], y[ok], "-o", color=c, lw=2, ms=6, mec="white", mew=1.5)
    first_none = np.where(~ok)[0].min()
    a.plot([kappas[first_none - 1], kappas[first_none]], [y[first_none - 1], 18], "--", color=c, lw=1.5)
    a.plot(kappas[~ok] + off, np.full((~ok).sum(), 18.0), "o", ms=7, mfc="white", mec=c, mew=2, clip_on=False)
    a.annotate(f"{name}: closes at {y[0]:.1f} y\nwhen T is fixed", (kappas[0], y[0]), xytext=(8, -4 if name == "boy" else 12),
               textcoords="offset points", color=c, fontsize=10, va="top" if name == "boy" else "bottom")
a.text(0.5, 17.35, "open circles: no closure before 18", color=MUTE, fontsize=9.5, ha="right", va="top")
a.axhline(18, color="#9ca3af", lw=1, ls=":")
a.text(0.5, 18.12, "age 18", color=MUTE, fontsize=9, ha="right")
a.axvline(0.5, color="#9ca3af", lw=1, ls="--")
a.text(0.485, 12.7, "same relative speed at every age\n(dynamic similarity, T ∝ √height)", color=MUTE, fontsize=9, ha="right", va="bottom")
a.set(xlim=(-0.02, 0.56), ylim=(12.5, 18.6), xlabel=r"how the 0.5 s fast curl scales with height:  $T\propto H^{\kappa}$",
      ylabel="window-closure age (years)", title="The closure age depends on one quiet assumption:\nthe fast curl lasts 0.5 s at every age")
a.set_xticks([0, 0.1, 0.2, 0.3, 0.4, 0.5]); a.set_xticklabels(["0\n(fixed, baseline)", "0.1", "0.2", "0.3", "0.4", "0.5\n(Froude)"])
a.grid(alpha=0.25)

b = ax[1]
masked = np.ma.masked_invalid(grid)
cmap = LinearSegmentedColormap.from_list("seq", ["#e8f0fa", "#9fc0e6", "#4a86c8", "#1f5fa8", "#12396b"]).reversed()
b.set_facecolor("#e5e7eb")
im = b.pcolormesh(shares, tols, masked, cmap=cmap, shading="nearest", vmin=4, vmax=18)
cs = b.contour(shares, tols, masked, levels=[6, 8, 10, 12, 14, 16], colors="white", linewidths=1.0)
b.clabel(cs, fmt="%d y", fontsize=8.5)
b.plot(2.0, 100, "o", ms=11, mfc="none", mec=INK, mew=2)
b.annotate("baseline\n(13.9 y)", (2.0, 100), xytext=(-62, -34), textcoords="offset points", fontsize=10, arrowprops=dict(arrowstyle="-", color=INK, lw=1))
b.text(3.45, 188, "grey = no closure before 18", color=MUTE, fontsize=9.5, ha="right", va="top")
b.set(xlabel="object carried (% of body mass)", ylabel="pressure tolerance (kPa)",
      title="Object mass and tolerance are one knob:\nclosure depends mostly on their ratio")
cb = fig.colorbar(im, ax=b, pad=0.02); cb.set_label("closure age, median boy (years)"); cb.outline.set_visible(False)
fig.text(0.01, 0.005, "Team 26126 model, unchanged; only the duration scaling and the load/tolerance values vary.  Scaled load (object = share of body mass), "
         "loosest safe fit; right panel: median boy, fixed 0.5 s curl.", fontsize=8.5, color=MUTE)
fig.tight_layout(rect=(0, 0.02, 1, 1))
(ROOT / "figures").mkdir(exist_ok=True); (ROOT / "results").mkdir(exist_ok=True)
fig.savefig(ROOT / "figures" / "fig15_closure_hidden_assumptions.png", dpi=170, facecolor="white")
json.dump(dict(kappa=kappas.tolist(), boy=[None if np.isnan(v) else float(v) for v in boy], girl=[None if np.isnan(v) else float(v) for v in girl],
               shares_pct=shares.tolist(), tolerance_kPa=tols.tolist(),
               boy_map=[[None if np.isnan(v) else float(v) for v in row] for row in grid]),
          open(ROOT / "results" / "12_closure_hidden_assumptions.json", "w"))
print("wrote figures/fig15_closure_hidden_assumptions.png and results/12_closure_hidden_assumptions.json")
