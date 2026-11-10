from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.integrate import solve_ivp

from .config import Params, Task
from .dynamics import (build_arm, inverse_dynamics, newton_euler_moment, object_mass,
                       prosthetic_side, residual_limb)
from .growth import Child
from .kinematics import Trajectory, trajectory
from .prosthesis import InterfaceState, Socket, interface_state


@dataclass(frozen=True)
class SocketLoads:
    task: Task
    traj: Trajectory
    state: InterfaceState
    shoulder_torque: np.ndarray
    elbow_torque: np.ndarray
    shear: np.ndarray
    axial: np.ndarray
    moment: np.ndarray
    moment_pressure: np.ndarray

    @property
    def peak_pressure(self) -> np.ndarray:
        return self.state.fit_pressure + self.moment_pressure

    @property
    def pull_out(self) -> np.ndarray:
        return np.maximum(0.0, -self.axial)


@dataclass(frozen=True)
class WorstCase:
    state: InterfaceState
    peak_pressure: float
    moment_pressure: float
    pull_out: float
    critical_task: str
    tolerance: float
    friction: float

    @property
    def stress_index(self) -> float:
        return self.peak_pressure / self.tolerance

    @property
    def friction_capacity(self) -> float:
        return self.friction * self.state.fit_pressure * self.state.contact_area

    @property
    def suspension_margin(self) -> float:
        return self.friction_capacity / max(self.pull_out, 1e-12)

    @property
    def failed(self) -> bool:
        return self.stress_index > 1.0 or self.suspension_margin < 1.0


def edge_line_loads(shear, moment, length):
    proximal = 4.0 * shear / length - 6.0 * moment / length**2
    distal = -2.0 * shear / length + 6.0 * moment / length**2
    return proximal, distal


def line_load_to_pressure(line_load, radius):
    return 2.0 * np.abs(line_load) / (np.pi * radius)


def socket_loads(task: Task, child: Child, socket: Socket, age: float, p: Params, n: int = 201) -> SocketLoads:
    state = interface_state(child, socket, age, p)
    traj = trajectory(task, p, n)
    distal = prosthetic_side(socket, state, p)
    arm = build_arm(state.body, [residual_limb(state, p)] + distal, p)
    tau1, tau2 = inverse_dynamics(arm, traj)
    force, moment = newton_euler_moment(arm.L1, traj, distal, pivot=state.offset)
    phi = traj.forearm_angle.q
    shear = force[0] * np.cos(phi) + force[1] * np.sin(phi)
    axial = force[0] * np.sin(phi) - force[1] * np.cos(phi)
    proximal, distal_edge = edge_line_loads(shear, moment, state.engaged_length)
    pressure = line_load_to_pressure(np.maximum(np.abs(proximal), np.abs(distal_edge)), state.radius)
    return SocketLoads(task, traj, state, tau1, tau2, shear, axial, moment, pressure)


# Run all four actions and keep the worst one. In practice that is almost always the fast curl.
def worst_case(child: Child, socket: Socket, age: float, p: Params, n: int = 81) -> WorstCase:
    runs = [socket_loads(task, child, socket, age, p, n) for task in p.tasks]
    critical = max(runs, key=lambda r: r.peak_pressure.max())
    return WorstCase(
        state=runs[0].state,
        peak_pressure=float(critical.peak_pressure.max()),
        moment_pressure=float(max(r.moment_pressure.max() for r in runs)),
        pull_out=float(max(r.pull_out.max() for r in runs)),
        critical_task=critical.task.name,
        tolerance=p.pressure_tolerance,
        friction=p.friction,
    )


@dataclass(frozen=True)
class Pistoning:
    t: np.ndarray
    slip: np.ndarray
    quasi_static: np.ndarray
    stiffness: float
    natural_frequency: float


# Pistoning check: is it fair to treat the socket as sitting still on the limb? Model it as a mass on a spring and
# damper and look at how much it slips. See scripts/09_verification.py.
def interface_stiffness(state: InterfaceState, p: Params) -> float:
    shear_modulus = p.tissue_modulus / 3.0
    thickness = p.soft_tissue_fraction * state.radius
    stiffening = np.exp(p.tissue_stiffening * max(state.tissue_strain, 0.0))
    return shear_modulus * state.contact_area / thickness * stiffening


def pistoning(task: Task, child: Child, socket: Socket, age: float, p: Params) -> Pistoning:
    loads = socket_loads(task, child, socket, age, p, n=401)
    state = loads.state
    m = p.prosthesis_mass + object_mass(state.body, p)
    k = interface_stiffness(state, p)
    c = 2.0 * p.interface_damping * np.sqrt(k * m)
    t, a = loads.traj.t, loads.axial
    sol = solve_ivp(lambda time, x: [x[1], (-np.interp(time, t, a) - c * x[1] - k * x[0]) / m],
                    (t[0], t[-1]), [-a[0] / k, 0.0], t_eval=t, rtol=1e-10, atol=1e-13, max_step=t[1] - t[0])
    return Pistoning(t, sol.y[0], -a / k, k, float(np.sqrt(k / m) / (2 * np.pi)))
