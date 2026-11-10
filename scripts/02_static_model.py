import numpy as np
import matplotlib.pyplot as plt

from common import BASE, BOY, CHILDREN, GROWING
from pedsocket import design_socket, interface_state
from pedsocket.analytic import fresh_socket_static_pressure, leading_order_pressure, power_law, static_hold_pressure
from pedsocket.plotting import record, save, sex_color

ages = np.linspace(5, 17, 49)
fig, ax = plt.subplots(1, 3, figsize=(15, 4.3))
summary = {}
anchors = {}
for child in CHILDREN:
    col = sex_color(child.sex)
    exact = np.array([fresh_socket_static_pressure(child, a, BASE) for a in ages])
    lead = np.array([leading_order_pressure(design_socket(child, a, BASE), a, child, BASE) for a in ages])
    grow = np.array([fresh_socket_static_pressure(child, a, GROWING) for a in ages])
    ax[0].plot(ages, exact / 1e3, color=col, lw=2.2, label=f"{child.sex}: exact")
    ax[0].plot(ages, lead / 1e3, "--", color=col, lw=1.4, label=f"{child.sex}: leading order $12M/\\pi r L^2$")
    ax[0].plot(ages, grow / 1e3, ":", color=col, lw=2.2, label=f"{child.sex}: load = 2% body mass")
    mh = np.array([interface_state(child, design_socket(child, a, BASE), a, BASE).body for a in ages])
    MH = np.array([b.mass * b.height for b in mh])
    M_over_H = np.array([b.mass / b.height for b in mh])
    anchors.setdefault("fixed", (MH[0], exact[0] / 1e3))
    k_fixed, _ = power_law(MH, exact)
    no_object = np.array([fresh_socket_static_pressure(child, a, GROWING.updated(object_fraction=0.0)) for a in ages])
    object_part = grow - no_object
    ax[1].loglog(MH, exact / 1e3, "o", ms=3, color=col, label=f"{child.sex}: slope {k_fixed:.3f}")
    ax[2].plot(ages, no_object / 1e3, "--", color=col, lw=1.4, label=f"{child.sex}: prosthesis term $\\propto$ (MH)$^{{-1/2}}$")
    ax[2].plot(ages, object_part / 1e3, ":", color=col, lw=2, label=f"{child.sex}: object term $\\propto$ (M/H)$^{{1/2}}$")
    ax[2].plot(ages, grow / 1e3, color=col, lw=2.2, label=f"{child.sex}: total")
    k_obj, _ = power_law(M_over_H, object_part)
    k_pro, _ = power_law(MH, no_object)
    cross = ages[np.argmax(object_part > 2 * no_object)] if np.any(object_part > 2 * no_object) else np.nan
    summary[child.sex] = dict(slope_fixed=k_fixed, slope_object_term=k_obj, slope_prosthesis_term=k_pro,
                              max_rel_error_leading=float(np.max(np.abs(lead - exact) / exact)),
                              age_object_term_twice_prosthesis=float(cross))
    print(f"  {child.sex}: fixed-load slope {k_fixed:.4f}; object term slope {k_obj:.4f}; prosthesis term slope {k_pro:.4f}")
x0, y0 = anchors["fixed"]
x = np.array(ax[1].get_xlim())
ax[1].loglog(x, y0 * (x / x0) ** -0.5, "k--", lw=1, label="scaling theory: slope −1/2")
ax[0].set(xlabel="age at fitting (years)", ylabel="kPa", title="Model 0: static hold, new socket")
ax[1].set(xlabel="M·H  (kg·m)", ylabel="kPa", title="Same 0.5 kg object: p $\\propto$ (MH)$^{-1/2}$")
ax[2].set(xlabel="age at fitting (years)", ylabel="kPa", title="Load = 2% body mass: two-term law")
ax[0].legend(fontsize=8)
ax[1].legend(fontsize=8)
ax[2].legend(fontsize=7, loc="center", bbox_to_anchor=(0.5, 0.37), ncol=2, columnspacing=1.0, handlelength=1.8)  # sits in the empty band between the curves
save(fig, "fig02_static_model")
socket = design_socket(BOY, 8.0, BASE)
summary["boy_age8_static_kPa"] = static_hold_pressure(socket, 8.0, BOY, BASE) / 1e3
record("02_static_model", summary)
