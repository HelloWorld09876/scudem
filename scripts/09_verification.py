import numpy as np
import matplotlib.pyplot as plt

from common import BASE, BOY, FIT_AGE
from pedsocket import body_at, design_socket, interface_state
from pedsocket.dynamics import (build_arm, forward_dynamics, intact_forearm, inverse_dynamics, mechanical_energy,
                                newton_euler_moment, prosthetic_side, residual_limb)
from pedsocket.interface import pistoning
from pedsocket.kinematics import trajectory
from pedsocket.plotting import record, save

body = body_at(BOY, 10.0, BASE)
passive = build_arm(body, intact_forearm(body, BASE), BASE)
t = np.linspace(0, 3, 3001)
zero = np.zeros_like(t)
sol = forward_dynamics(passive, t, zero, zero, [0.6, 0.9, 0.0, 0.0], rtol=1e-11)
energy = mechanical_energy(passive, sol.y)
drift = np.abs(energy - energy[0]) / abs(energy[0])

socket = design_socket(BOY, FIT_AGE, BASE)
state = interface_state(BOY, socket, FIT_AGE, BASE)
forearm = [residual_limb(state, BASE)] + prosthetic_side(socket, state, BASE)
arm = build_arm(state.body, forearm, BASE)
traj = trajectory(BASE.task("Lift to shelf"), BASE, 401)
tau1, tau2 = inverse_dynamics(arm, traj)
replay = forward_dynamics(arm, traj.t, tau1, tau2, [traj.shoulder.q[0], traj.elbow.q[0], 0.0, 0.0])
angle_error = np.degrees(max(np.abs(replay.y[0] - traj.shoulder.q).max(), np.abs(replay.y[1] - traj.elbow.q).max()))
_, ne = newton_euler_moment(arm.L1, traj, forearm, pivot=0.0)
ne_error = float(np.max(np.abs(ne - tau2)))
pis = pistoning(BASE.task("Fast curl"), BOY, socket, FIT_AGE, BASE)

fig, ax = plt.subplots(1, 3, figsize=(16, 4.3))
ax[0].semilogy(t, np.maximum(drift, 1e-16), color="#1f5fa8", lw=1.5)
ax[0].set(xlabel="time (s)", ylabel="relative energy drift", title="Passive arm: energy is conserved")
ax[1].plot(traj.t, np.degrees(traj.shoulder.q), color="#9ca3af", lw=4, label="prescribed (minimum jerk)")
ax[1].plot(traj.t, np.degrees(traj.elbow.q), color="#9ca3af", lw=4)
ax[1].plot(replay.t, np.degrees(replay.y[0]), "--", color="#c2410c", lw=1.6, label="shoulder, ODE replay")
ax[1].plot(replay.t, np.degrees(replay.y[1]), "--", color="#1f5fa8", lw=1.6, label="elbow, ODE replay")
ax[1].set(xlabel="time (s)", ylabel="degrees", title=f"Torques → ODE → same motion (max error {angle_error:.3f}°)")
ax[1].legend(fontsize=8.5)
ax[2].plot(pis.t, 1000 * pis.slip, "k", lw=2, label="pistoning ODE")
ax[2].plot(pis.t, 1000 * pis.quasi_static, "--", color="#dc2626", lw=1.4, label="quasi-static  −A/k")
ax[2].set(xlabel="time (s)", ylabel="mm", title=f"Socket slip, fast curl: $f_n$ = {pis.natural_frequency:.0f} Hz")
ax[2].legend(fontsize=8.5)
save(fig, "fig13_verification")
print(f"  energy drift {drift.max():.1e}; replay error {angle_error:.4f}°; Newton–Euler vs Lagrange {ne_error:.1e} N·m")
print(f"  pistoning k = {pis.stiffness / 1e3:.1f} kN/m, f_n = {pis.natural_frequency:.1f} Hz, max slip {1000 * pis.slip.max():.2f} mm")
record("09_verification", dict(energy_drift=float(drift.max()), replay_error_deg=float(angle_error),
                               newton_euler_error_Nm=ne_error, pistoning_k_kN=pis.stiffness / 1e3,
                               pistoning_fn_Hz=pis.natural_frequency, max_slip_mm=float(1000 * pis.slip.max()),
                               dynamic_error_mm=float(1000 * np.max(np.abs(pis.slip - pis.quasi_static)))))
