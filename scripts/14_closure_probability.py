"""Window closure as a probability, not a single age.

The baseline closure ages (13.9 y boys, 14.6 y girls) come from one hand-picked set of inputs. Here we sample the nine
uncertain inputs of script 07 PLUS the two assumptions that script 12 found to matter most:
  * object_fraction  : the everyday object as a share of body mass, 1%-3%,
  * kappa            : how movement time scales with height, T ~ H**kappa, from -0.1 (older children move faster) to 0.3
                       (kappa = 0 is the baseline "0.5 s at every age"; kappa = 0.5 would be dynamic similarity),
and we run two readings of how the residual limb grows after the first fitting at age 6:
  A  "as assumed"  : every new socket is made for a limb that is 45% (sampled) of the forearm at that age (the original baseline),
  B  "self-consistent": the limb is that share only at age 6 and then grows at the proximal-growth share of forearm growth
                       (the rule the model itself uses after fitting).
Result: the cumulative distribution of the closure age, including the share of samples that never close before 18.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import qmc, spearmanr

from common import BOY, GROWING
from pedsocket import body_at
from pedsocket.lifetime import limb_grows_by_rule, window_closure_age
from pedsocket.plotting import record, save
from pedsocket.uncertainty import UNCERTAIN

N, SEED = 600, 26126
EXTRA = {"object_fraction": (0.01, 0.03), "kappa": (-0.1, 0.3)}
RANGES = {**UNCERTAIN, **EXTRA}
NAMES = list(RANGES)
LABELS = {
    "tissue_modulus": "tissue modulus E", "tissue_stiffening": "tissue stiffening B", "pressure_tolerance": "pressure tolerance",
    "friction": "skin–socket friction", "prosthesis_mass": "prosthesis mass", "residual_fraction": "residual-limb length",
    "soft_tissue_fraction": "soft-tissue thickness", "atrophy_ratio": "residual-limb radius",
    "proximal_growth_share": "proximal growth share", "object_fraction": "object share of body mass",
    "kappa": "movement-time exponent κ",
}
lo = np.array([RANGES[k][0] for k in NAMES])
hi = np.array([RANGES[k][1] for k in NAMES])
samples = qmc.scale(qmc.LatinHypercube(d=len(NAMES), seed=SEED).random(N), lo, hi)
H10 = body_at(BOY, 10.0, GROWING).height


def closure(row, rule):
    d = dict(zip(NAMES, row))
    kappa, f = d.pop("kappa"), d.pop("object_fraction")
    p = GROWING.updated(object_fraction=f, **d)
    base_at = limb_grows_by_rule(BOY, p, 6.0) if rule == "B" else (lambda a: p)
    at = lambda a: base_at(a).updated(speed_factor=float((body_at(BOY, a, p).height / H10) ** (-kappa)))
    return window_closure_age(BOY, p, params_at=at)


out = {}
for rule in ("A", "B"):
    out[rule] = np.array([closure(r, rule) for r in samples])
    print(f"  rule {rule}: done")

ages = np.arange(4.0, 18.01, 0.25)
summary = {"n": N, "ranges": {k: list(v) for k, v in RANGES.items()}}
fig, ax = plt.subplots(1, 3, figsize=(17, 5.0))
colors = {"A": "#1f5fa8", "B": "#c2410c"}
titles = {"A": "as assumed (limb = 45% of forearm at every fitting age)",
          "B": "self-consistent (limb grows at the proximal share after age 6)"}
for rule in ("A", "B"):
    c = out[rule]
    never = float(np.mean(~np.isfinite(c)))
    cdf = np.array([np.mean(c <= a) for a in ages])
    ax[0].step(ages, 100 * cdf, where="post", color=colors[rule], lw=2.4, label=titles[rule])
    coded_never = np.where(np.isfinite(c), c, 18.5)      # 'never closes before 18' counted as later than any closure
    s = dict(never=never, closed_at_4=float(np.mean(c <= 4.0)), p_by_10=float(np.mean(c <= 10.0)), p_by_12=float(np.mean(c <= 12.0)),
             p_by_14=float(np.mean(c <= 14.0)), p_by_16=float(np.mean(c <= 16.0)),
             median_all=float(np.median(coded_never)), q10=float(np.quantile(coded_never, 0.10)), q90=float(np.quantile(coded_never, 0.90)))
    # Spearman over all samples, with "never" coded as 18.5 (later than any observed closure).
    coded = np.where(np.isfinite(c), c, 18.5)
    s["spearman"] = {n: float(spearmanr(samples[:, i], coded).statistic) for i, n in enumerate(NAMES)}
    # How the answer depends on the two assumptions we cannot pin down.
    f_bins = np.array([0.01, 0.015, 0.02, 0.025, 0.03])
    f_idx = np.digitize(samples[:, NAMES.index("object_fraction")], f_bins[1:-1])
    k_bins = np.array([-0.1, 0.0, 0.1, 0.2, 0.3])
    k_idx = np.digitize(samples[:, NAMES.index("kappa")], k_bins[1:-1])
    s["p_close_given_f"] = [float(np.mean(np.isfinite(c[f_idx == j]))) for j in range(4)]
    s["p_close_given_kappa"] = [float(np.mean(np.isfinite(c[k_idx == j]))) for j in range(4)]
    summary[rule] = s
    print(f"  {rule}: never {100 * never:.0f}%, closed by 12 y {100 * s['p_by_12']:.0f}%, by 14 y {100 * s['p_by_14']:.0f}%, "
          f"median {s['median_all']:.1f} y (10–90%: {s['q10']:.1f}–{s['q90']:.1f}; 18.5 means never)")
    print("     P(closes before 18 | object share bins 1–1.5–2–2.5–3%): "
          + ", ".join(f"{100 * v:.0f}%" for v in s["p_close_given_f"]))
    print("     P(closes before 18 | kappa bins -0.1–0–0.1–0.2–0.3): "
          + ", ".join(f"{100 * v:.0f}%" for v in s["p_close_given_kappa"]))
    top = sorted(s["spearman"], key=lambda n: -abs(s["spearman"][n]))[:4]
    print("     strongest drivers: " + ", ".join(f"{LABELS[n]} ({s['spearman'][n]:+.2f})" for n in top))
    ax[0].axhline(100 * (1 - never), color=colors[rule], ls=":", lw=1.1)
ax[0].axvline(13.9, color="#374151", ls="--", lw=1.2)
ax[0].text(13.95, 4, "original baseline\n(boy, 13.9 y)", fontsize=8.5, color="#374151")
ax[0].set(xlabel="age (years)", ylabel="% of samples whose window has closed by this age", ylim=(0, 100), xlim=(4, 18),
          title=f"Closure is a distribution ({N} samples, boys)")
ax[0].legend(fontsize=8.2, loc="upper left")
for k, (rule, w) in enumerate((("A", -0.2), ("B", 0.2))):
    j = np.arange(4)
    ax[1].bar(j + w, [100 * v for v in summary[rule]["p_close_given_f"]], 0.4, color=colors[rule], alpha=0.85,
              label=f"{rule}: {'as assumed' if rule == 'A' else 'self-consistent'}")
ax[1].set_xticks(np.arange(4), ["1–1.5", "1.5–2", "2–2.5", "2.5–3"])
ax[1].set(xlabel="object share of body mass (%)", ylabel="% of samples that close before 18", ylim=(0, 100),
          title="The load share decides whether it happens at all")
ax[1].legend(fontsize=8.5, loc="upper left")
order = sorted(NAMES, key=lambda n: abs(summary["B"]["spearman"][n]) + abs(summary["A"]["spearman"][n]))
yy = np.arange(len(order))
ax[2].barh(yy - 0.2, [summary["A"]["spearman"][n] for n in order], 0.4, color=colors["A"], label="A")
ax[2].barh(yy + 0.2, [summary["B"]["spearman"][n] for n in order], 0.4, color=colors["B"], label="B")
ax[2].set_yticks(yy, [LABELS[n] for n in order])
ax[2].axvline(0, color="k", lw=1)
ax[2].set(xlabel="Spearman rank correlation with closure age (positive = closes later)", title="What moves the closure age")
ax[2].legend(fontsize=8.5, loc="lower right")
save(fig, "fig17_closure_probability")
record("14_closure_probability", summary)
