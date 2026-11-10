import numpy as np
import matplotlib.pyplot as plt

from common import BASE, CENTILES, CHILDREN
from pedsocket import Child, design_socket
from pedsocket.interface import worst_case
from pedsocket.lifetime import replacement_schedule
from pedsocket.plotting import LIMIT, record, save, sex_color

START, END = 6.0, 18.0
summary = {}
fig, ax = plt.subplots(1, 2, figsize=(14, 4.6), sharey=True)
for k, child in enumerate(CHILDREN):
    for policy, ls, col, label in [("standard", "-", sex_color(child.sex), "standard fit (5% tissue strain)"),
                                   ("growth", "--", "k", "growth-allowance fit")]:
        schedule = replacement_schedule(child, START, END, BASE, policy)
        for j, life in enumerate(schedule):
            stop = END if life.outlasts_growth else min(life.fit_age + life.years, END)
            socket = design_socket(child, life.fit_age, BASE, life.fit_strain)
            ages = np.linspace(life.fit_age, stop, 30)
            ax[k].plot(ages, [worst_case(child, socket, a, BASE).stress_index for a in ages], ls, color=col, lw=1.8,
                       label=label if j == 0 else None)
        summary[f"{child.sex}_{policy}"] = dict(count=len(schedule), fit_ages=[s.fit_age for s in schedule],
                                                fit_strains=[s.fit_strain for s in schedule])
        print(f"  {child.sex:4s} {policy:8s}: {len(schedule)} sockets at " + ", ".join(f"{s.fit_age:.1f}" for s in schedule))
    ax[k].axhline(1.0, color=LIMIT, ls="--", lw=1.2)
    ax[k].text(START + 0.1, 0.975, "replace when SSI = 1", color=LIMIT, fontsize=9, va="top")
    ax[k].set(xlabel="age (years)", title=f"{child.sex}: every socket from age {START:g} to {END:g}")
    ax[k].legend(fontsize=9, loc="lower left")
ax[0].set_ylabel("Socket Stress Index  $p_{peak}/p_{tol}$")
save(fig, "fig08_replacement_schedule")

centile_table = {}
for sex in ("boy", "girl"):
    for name, z in CENTILES.items():
        child = Child(sex, z)
        counts = {policy: len(replacement_schedule(child, START, END, BASE, policy)) for policy in ("standard", "growth")}
        centile_table[f"{sex}_{name}"] = counts
        print(f"  {sex:4s} {name:4s} centile: standard {counts['standard']}, growth-allowance {counts['growth']}")
summary["centiles"] = centile_table
record("05_replacement_policy", summary)
