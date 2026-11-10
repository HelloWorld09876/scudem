import numpy as np
import matplotlib.pyplot as plt

from common import BASE, BOY, FIT_AGE
from pedsocket import design_socket
from pedsocket.lifetime import socket_lifetime
from pedsocket.msk import musculoskeletal
from pedsocket.plotting import record, save

socket = design_socket(BOY, FIT_AGE, BASE)
replace_at = FIT_AGE + socket_lifetime(BOY, FIT_AGE, BASE).years
ages = np.linspace(FIT_AGE, FIT_AGE + 4, 41)
M = [musculoskeletal(BOY, socket, a, BASE) for a in ages]
fig, ax = plt.subplots(1, 3, figsize=(15, 4.3))
ax[0].plot(ages, [100 * m.reach_deficit for m in M], "k", lw=2.2)
ax[0].set(xlabel="age (years)", ylabel="cm", title="Prosthetic arm shorter than intact arm")
ax[1].plot(ages, [m.trunk_lean_deg for m in M], color="#7c3aed", lw=2.2, label="trunk lean to reach (deg)")
ax[1].plot(ages, [m.lumbar_moment_pct for m in M], color="#15803d", lw=2.2, label="extra L5/S1 moment (% BW·H)")
ax[1].set(xlabel="age (years)", title="Compensation moves to the trunk")
ax[1].legend(fontsize=9)
for attr, label, col, ls in [("elbow_effort_prosthetic", "elbow, prosthetic", "#c2410c", "-"),
                             ("elbow_effort_intact", "elbow, intact", "#c2410c", ":"),
                             ("shoulder_effort_prosthetic", "shoulder, prosthetic", "#1f5fa8", "-"),
                             ("shoulder_effort_intact", "shoulder, intact", "#1f5fa8", ":")]:
    ax[2].plot(ages, [100 * getattr(m, attr) for m in M], ls, color=col, lw=2, label=label)
ax[2].set(xlabel="age (years)", ylabel="% of maximum strength", title="Joint effort, worst action")
ax[2].legend(fontsize=8.5)
for a in ax:
    a.axvline(replace_at, color="#dc2626", lw=1, ls="--")
ax[0].text(replace_at + 0.05, 0.3, "socket\nreplaced\nhere", color="#dc2626", fontsize=8.5)
save(fig, "fig12_musculoskeletal")
at = {f"{a:.0f}": dict(deficit_cm=100 * m.reach_deficit, lean_deg=m.trunk_lean_deg, lumbar_pct=m.lumbar_moment_pct,
                       elbow_p=m.elbow_effort_prosthetic, elbow_i=m.elbow_effort_intact,
                       shoulder_p=m.shoulder_effort_prosthetic, shoulder_i=m.shoulder_effort_intact)
      for a, m in zip(ages, M) if abs(a - round(a)) < 1e-9}
for k, v in at.items():
    print(f"  age {k}: deficit {v['deficit_cm']:.1f} cm, lean {v['lean_deg']:.1f}°, lumbar +{v['lumbar_pct']:.2f}% BW·H")
deficit_at_replacement = musculoskeletal(BOY, socket, replace_at, BASE)
record("08_musculoskeletal", dict(by_age=at, replace_age=replace_at,
                                  deficit_at_replacement_cm=100 * deficit_at_replacement.reach_deficit,
                                  lean_at_replacement_deg=deficit_at_replacement.trunk_lean_deg))
