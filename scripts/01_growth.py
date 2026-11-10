import numpy as np
import matplotlib.pyplot as plt

from common import CENTILES, CHILDREN
from pedsocket import Child, body_at, load_params
from pedsocket.plotting import record, save, sex_color

p = load_params()
ages = np.linspace(4, 20, 400)
fig, ax = plt.subplots(1, 3, figsize=(15, 4.3))
summary = {}
for child in CHILDREN:
    col = sex_color(child.sex)
    for name, z in CENTILES.items():
        c = child if z == 0 else Child(child.sex, z)
        ax[0].plot(ages, 100 * c.height(ages), color=col, lw=2.2 if z == 0 else 1.0, alpha=1 if z == 0 else 0.55)
    ax[0].plot(child.data_ages[::6], child.data_heights_cm[::6], "o", ms=3.5, color=col, mfc="white",
               label=f"{child.sex}: CDC 2000 median")
    v = 100 * child.growth_velocity(ages)
    ax[1].plot(ages, v, color=col, lw=2.2, label=child.sex)
    phv_age, phv = child.peak_height_velocity()
    ax[1].annotate(f"PHV {phv:.1f} cm/yr\nat {phv_age:.1f} y", (phv_age, phv), xytext=(8, -4),
                   textcoords="offset points", color=col, fontsize=9)
    bodies = [body_at(child, a, p) for a in ages]
    ax[2].plot(ages, [1000 * b.residual_radius for b in bodies], color=col, lw=2.2, label=child.sex)
    h1, h_theta, s0, s1, theta = child.pb
    summary[child.sex] = dict(h1=h1, h_theta=h_theta, s0=s0, s1=s1, theta=theta, rmse_cm=child.pb_rmse_cm,
                              phv_age=phv_age, phv_cm_per_yr=phv)
    print(f"  {child.sex}: h1={h1:.1f} hθ={h_theta:.1f} s0={s0:.3f} s1={s1:.3f} θ={theta:.2f}  RMSE={child.pb_rmse_cm:.2f} cm  PHV {phv:.1f} cm/yr @ {phv_age:.1f}")
ax[0].set(xlabel="age (years)", ylabel="height (cm)", title=r"$\dot H = s(t)\,(h_1 - H)$  vs CDC data (10/50/90th)")
ax[1].set(xlabel="age (years)", ylabel="cm / year", title="Growth velocity from the ODE")
ax[2].set(xlabel="age (years)", ylabel="mm", title=r"Residual-limb radius $r \propto \sqrt{M/H}$")
for a in ax:
    a.legend(fontsize=9)
save(fig, "fig01_growth")
record("01_growth", summary)
