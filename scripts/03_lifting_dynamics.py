import numpy as np
import matplotlib.pyplot as plt

from common import BASE, BOY, CHILDREN, FIT_AGE
from pedsocket import design_socket, interface_state
from pedsocket.analytic import static_hold_pressure
from pedsocket.interface import socket_loads
from pedsocket.kinematics import dynamic_number, trajectory
from pedsocket.plotting import TASK_COLORS, LIMIT, record, save

socket = design_socket(BOY, FIT_AGE, BASE)
state = interface_state(BOY, socket, FIT_AGE, BASE)
L1 = state.body.upper_arm_length

fig, ax = plt.subplots(1, 4, figsize=(16, 4.4))
for k, task in enumerate(BASE.tasks):
    traj = trajectory(task, BASE, 201)
    for j, i in enumerate(np.linspace(0, 200, 6).astype(int)):
        a1, phi = traj.shoulder.q[i], traj.forearm_angle.q[i]
        elbow = L1 * np.array([np.sin(a1), -np.cos(a1)])
        axis = np.array([np.sin(phi), -np.cos(phi)])
        brim, hand = elbow + state.engaged_length * axis, elbow + state.grip_distance * axis
        alpha = 0.2 + 0.8 * j / 5
        ax[k].plot([0, elbow[0]], [0, elbow[1]], color="#9ca3af", lw=5, alpha=alpha, solid_capstyle="round")
        ax[k].plot([elbow[0], brim[0]], [elbow[1], brim[1]], color="#c2410c", lw=8, alpha=alpha, solid_capstyle="butt")
        ax[k].plot([brim[0], hand[0]], [brim[1], hand[1]], color="#1f5fa8", lw=4, alpha=alpha)
        ax[k].plot(*hand, "s", color="k", ms=7, alpha=alpha)
    ax[k].plot(0, 0, "o", color="k", ms=9)
    ax[k].set(xlim=(-0.15, 0.5), ylim=(-0.6, 0.48), aspect="equal", title=f"{task.name} ({task.duration:g} s)")
    ax[k].axis("off")
fig.suptitle("Action set (sagittal plane, shoulder fixed). Grey: upper arm · orange: residual limb in socket · "
             "blue: prosthesis · square: 0.5 kg object", fontsize=10.5)
save(fig, "fig03_actions")

fig, ax = plt.subplots(1, 3, figsize=(15, 4.3))
rows = {}
for task in BASE.tasks:
    r = socket_loads(task, BOY, socket, FIT_AGE, BASE)
    s = r.traj.t / r.traj.t[-1]
    col = TASK_COLORS[task.name]
    ax[0].plot(s, r.elbow_torque, color=col, lw=2, label=task.name)
    ax[1].plot(s, r.moment, color=col, lw=2)
    ax[2].plot(s, r.peak_pressure / 1e3, color=col, lw=2)
    rows[task.name] = dict(elbow_torque_Nm=float(np.abs(r.elbow_torque).max()),
                           shoulder_torque_Nm=float(np.abs(r.shoulder_torque).max()),
                           socket_moment_Nm=float(np.abs(r.moment).max()),
                           peak_pressure_kPa=float(r.peak_pressure.max() / 1e3),
                           pull_out_N=float(r.pull_out.max()))
    print(f"  {task.name:14s} elbow {rows[task.name]['elbow_torque_Nm']:.2f} N·m  socket moment "
          f"{rows[task.name]['socket_moment_Nm']:.2f} N·m  peak {rows[task.name]['peak_pressure_kPa']:.1f} kPa")
ax[2].axhline(BASE.pressure_tolerance / 1e3, color=LIMIT, ls="--", lw=1.2, label="tolerance")
ax[0].set(xlabel="normalised time", ylabel="N·m", title="Elbow torque (Lagrange equations)")
ax[1].set(xlabel="normalised time", ylabel="N·m", title="Moment carried by the socket")
ax[2].set(xlabel="normalised time", ylabel="kPa", title="Peak limb–socket pressure")
ax[0].legend(fontsize=9)
ax[2].legend(fontsize=9)
save(fig, "fig04_task_loads")

static = static_hold_pressure(socket, FIT_AGE, BOY, BASE)
pi_values, gains = [], []
for child in CHILDREN:
    for age in (6.0, 9.0, 12.0, 15.0):
        sock = design_socket(child, age, BASE)
        st = interface_state(child, sock, age, BASE)
        reference = static_hold_pressure(sock, age, child, BASE)
        for speed in (0.5, 0.75, 1.0, 1.5, 2.0, 2.5):
            p = BASE.updated(speed_factor=speed)
            for name in ("Slow curl", "Fast curl"):
                task = p.task(name)
                r = socket_loads(task, child, sock, age, p, 161)
                pi_values.append(dynamic_number(task, p, st.grip_distance))
                gains.append(r.moment_pressure.max() / reference)
pi_values, gains = np.array(pi_values), np.array(gains)
slope, intercept = np.polyfit(pi_values, gains, 1)
r2 = 1 - np.sum((gains - (slope * pi_values + intercept)) ** 2) / np.sum((gains - gains.mean()) ** 2)
fig, ax = plt.subplots(figsize=(6.5, 4.5))
# Slow curls (small Pi) do not follow the line: they give exactly the static-hold pressure, ratio 1. The line is a fit to the
# whole cloud, and most of the variance is at large Pi, so R^2 stays high even though the start of the curve is flat.
LOW_PI = 0.3
low = pi_values < LOW_PI
ax.axvspan(0, LOW_PI, color="#e5e7eb", alpha=0.7, zorder=0)
ax.plot(pi_values, gains, "o", ms=4, color="#1f5fa8", alpha=0.7, label="curl simulations (8 children×6 speeds×2 tasks)")
x = np.linspace(0, pi_values.max() * 1.05, 50)
ax.plot(x, slope * x + intercept, "k--", lw=1.4, label=f"straight-line fit: {intercept:.2f} + {slope:.2f}·Π   (R² = {r2:.3f})")
ax.annotate(f"slow curls (Π < {LOW_PI}):\nsame as holding still,\nratio ≈ 1", (LOW_PI * 0.5, 1.0), xytext=(2.6, 0.5), fontsize=8.5,
            arrowprops=dict(arrowstyle="-", color="#555", lw=0.8), color="#374151")
ax.set(xlabel=r"dynamic number  $\Pi = 5.77\,\Delta\theta\,L_p/(g\,T^2)$",
       ylabel="peak / static-hold pressure", title="Faster curls load the socket more")
ax.legend(fontsize=9, loc="upper left")
save(fig, "fig05_dynamic_collapse")
print(f"  amplification = {intercept:.3f} + {slope:.3f} Π   R² = {r2:.4f}")
line_error = np.abs(gains - (slope * pi_values + intercept))
print(f"  slow curls (Π < {LOW_PI}): {low.sum()} of {len(pi_values)}, ratio {gains[low].min():.3f}–{gains[low].max():.3f}; "
      f"straight line is off by up to {line_error.max():.2f}")
record("03_lifting_dynamics", dict(tasks=rows, static_hold_kPa=static / 1e3, collapse_intercept=intercept,
                                   collapse_slope=slope, collapse_r2=r2, upper_arm_m=L1,
                                   engaged_length_mm=1000 * state.engaged_length,
                                   grip_distance_mm=1000 * state.grip_distance, radius_mm=1000 * state.radius,
                                   collapse_points=int(len(pi_values)), low_pi_cutoff=LOW_PI, low_pi_points=int(low.sum()),
                                   low_pi_ratio_min=float(gains[low].min()), low_pi_ratio_max=float(gains[low].max()),
                                   collapse_max_line_error=float(line_error.max())))
