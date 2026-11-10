"""How firm is the window-closure age?

The headline result (the fit window for a median boy closes at about 13.9 years) comes out of a model with a few
assumptions that are easy to argue with. This script changes them one at a time and reports what happens to the closure age,
so the paper can say how much weight that number can carry.

Nothing here feeds the earlier steps. It only reads the baseline parameters and re-runs the closure search.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

from common import BASE, BOY, GIRL, GROWING
from pedsocket import body_at
from pedsocket.lifetime import limb_grows_by_rule, window_closure_age
from pedsocket.plotting import LIMIT, record, save, sex_color


def closure(child, p, params_at=None):
    value = window_closure_age(child, p, params_at=params_at)
    return float(value) if np.isfinite(value) else None


def say(value):
    return "no closure by 18" if value is None else f"{value:5.2f} y"


def height_scaled_mass(child, power):
    """Prosthesis mass that grows with the child: 0.40 kg at age 8, then proportional to height**power."""
    h8 = body_at(child, 8.0, BASE).height

    def params_at(age):
        ratio = body_at(child, age, BASE).height / h8
        return GROWING.updated(prosthesis_mass=BASE.prosthesis_mass * ratio ** power)

    return params_at


# Each case is (label, group, function that takes a child and returns the closure age).
cases = [("Baseline", "baseline", lambda c: closure(c, GROWING))]
for fraction in (0.015, 0.025, 0.030):
    cases.append((f"object = {100 * fraction:.1f}% of body mass", "load",
                  lambda c, f=fraction: closure(c, GROWING.updated(object_fraction=f))))
for tol in (75e3, 125e3):
    cases.append((f"pressure tolerance {tol / 1e3:.0f} kPa", "tolerance",
                  lambda c, t=tol: closure(c, GROWING.updated(pressure_tolerance=t))))
for ref in (6.0, 8.0):
    cases.append((f"limb follows the 25% growth rule from age {ref:g}", "limb",
                  lambda c, r=ref: closure(c, GROWING, limb_grows_by_rule(c, GROWING, r))))
cases.append(("prosthesis mass grows with height", "prosthesis", lambda c: closure(c, GROWING, height_scaled_mass(c, 1))))
cases.append(("prosthesis mass grows with height³", "prosthesis", lambda c: closure(c, GROWING, height_scaled_mass(c, 3))))
no_fast = tuple(t for t in BASE.tasks if t.name != "Fast curl")
cases.append(("without the fast curl", "task", lambda c: closure(c, GROWING.updated(tasks=no_fast))))

results = {}
for label, group, run in cases:
    boy, girl = run(BOY), run(GIRL)
    results[label] = dict(group=group, boy=boy, girl=girl)
    print(f"  {label:52s} boy {say(boy):>17s}   girl {say(girl):>17s}")

# Who sets the closure? Run each action on its own.
alone = {}
for task in BASE.tasks:
    p = GROWING.updated(tasks=(task,))
    alone[task.name] = dict(boy=closure(BOY, p), girl=closure(GIRL, p))
    print(f"  only {task.name:47s} boy {say(alone[task.name]['boy']):>17s}   girl {say(alone[task.name]['girl']):>17s}")

# Figure: one row per assumption, boy and girl side by side. Bars that would run past 18 are hatched and labelled.
fig, ax = plt.subplots(figsize=(10.5, 6.2))
labels = list(results)[::-1]
y = np.arange(len(labels))
for offset, sex in ((0.2, "boy"), (-0.2, "girl")):
    for yi, label in zip(y, labels):
        value = results[label][sex]
        shown = 18.0 if value is None else value
        ax.barh(yi + offset, shown, 0.38, color=sex_color(sex),
                alpha=0.35 if value is None else 1.0, hatch="//" if value is None else None)
        ax.text(shown + 0.12, yi + offset, "open at 18" if value is None else f"{value:.1f}", va="center", fontsize=8.5)
ax.axvline(results["Baseline"]["boy"], color=sex_color("boy"), ls=":", lw=1.2)
ax.axvline(results["Baseline"]["girl"], color=sex_color("girl"), ls=":", lw=1.2)
ax.set_yticks(y, labels)
ax.set(xlim=(0, 20), xlabel="window-closure age (years)",
       title="The closure age moves a lot when one assumption changes")
ax.legend(handles=[Patch(color=sex_color("boy"), label="boy, 50th centile"), Patch(color=sex_color("girl"), label="girl, 50th centile"),
                   Patch(facecolor="#d1d5db", hatch="//", label="no closure before 18")],
          fontsize=9, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=3)
save(fig, "fig14_closure_sensitivity")

record("11_closure_sensitivity", dict(cases=results, one_action_only=alone))
