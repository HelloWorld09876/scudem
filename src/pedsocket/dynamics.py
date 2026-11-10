from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.integrate import solve_ivp

from .body import Body, body_at
from .config import Params
from .growth import Child
from .kinematics import Trajectory
from .prosthesis import InterfaceState, Socket

G = 9.81


@dataclass(frozen=True)
class PointBody:
    mass: float
    position: float
    inertia: float


@dataclass(frozen=True)
class ArmModel:
    m1: float
    c1: float
    I1: float
    L1: float
    m2: float
    c2: float
    I2: float


# Two ways to load the child: a fixed object at every age (0.5 kg), or an object that grows with the child (a fixed
# fraction of body mass). The window-closure result only exists in the second case.
def object_mass(body: Body, p: Params) -> float:
    return p.object_mass if p.load_mode == "fixed" else p.object_fraction * body.mass


def lumped(bodies: list[PointBody]) -> tuple[float, float, float]:
    m = sum(b.mass for b in bodies)
    c = sum(b.mass * b.position for b in bodies) / m
    I = sum(b.inertia + b.mass * (b.position - c) ** 2 for b in bodies)
    return m, c, I


def intact_forearm(body: Body, p: Params) -> list[PointBody]:
    return [
        PointBody(body.forearm_mass, p.forearm_com * body.forearm_length,
                  body.forearm_mass * (p.forearm_gyration * body.forearm_length) ** 2),
        PointBody(body.hand_mass, body.grip_distance, 0.0),
        PointBody(object_mass(body, p), body.grip_distance, 0.0),
    ]


def residual_limb(state: InterfaceState, p: Params) -> PointBody:
    b = state.body
    m = b.forearm_mass * (state.residual_length / b.forearm_length) * p.atrophy_ratio**2
    return PointBody(m, 0.5 * state.residual_length, m * state.residual_length**2 / 12.0)


def prosthetic_side(socket: Socket, state: InterfaceState, p: Params) -> list[PointBody]:
    s, length = state.offset, socket.prosthesis_length
    return [
        PointBody(p.prosthesis_mass, s + p.prosthesis_com * length,
                  p.prosthesis_mass * (p.prosthesis_gyration * length) ** 2),
        PointBody(object_mass(state.body, p), state.grip_distance, 0.0),
    ]


def build_arm(body: Body, forearm: list[PointBody], p: Params) -> ArmModel:
    L1 = body.upper_arm_length
    m2, c2, I2 = lumped(forearm)
    return ArmModel(body.upper_arm_mass, p.upper_arm_com * L1,
                    body.upper_arm_mass * (p.upper_arm_gyration * L1) ** 2, L1, m2, c2, I2)


def mass_matrix(arm: ArmModel, q2):
    cos2 = np.cos(q2)
    M11 = arm.I1 + arm.m1 * arm.c1**2 + arm.I2 + arm.m2 * (arm.L1**2 + arm.c2**2 + 2 * arm.L1 * arm.c2 * cos2)
    M12 = arm.I2 + arm.m2 * (arm.c2**2 + arm.L1 * arm.c2 * cos2)
    M22 = arm.I2 + arm.m2 * arm.c2**2
    return M11, M12, M22


def coupling(arm: ArmModel, q2):
    return arm.m2 * arm.L1 * arm.c2 * np.sin(q2)


def gravity(arm: ArmModel, q1, q2):
    g1 = G * (arm.m1 * arm.c1 * np.sin(q1) + arm.m2 * (arm.L1 * np.sin(q1) + arm.c2 * np.sin(q1 + q2)))
    g2 = G * arm.m2 * arm.c2 * np.sin(q1 + q2)
    return g1, g2


# We prescribe the motion and solve for the torques that would produce it (inverse dynamics). forward_dynamics goes the
# other way and is only used to check that those torques reproduce the motion.
def inverse_dynamics(arm: ArmModel, traj: Trajectory):
    q1, q2 = traj.shoulder, traj.elbow
    M11, M12, M22 = mass_matrix(arm, q2.q)
    h = coupling(arm, q2.q)
    g1, g2 = gravity(arm, q1.q, q2.q)
    tau1 = M11 * q1.qdd + M12 * q2.qdd - h * (2 * q1.qd * q2.qd + q2.qd**2) + g1
    tau2 = M12 * q1.qdd + M22 * q2.qdd + h * q1.qd**2 + g2
    return tau1, tau2


def accelerations(arm: ArmModel, state, tau1, tau2):
    q1, q2, w1, w2 = state
    M11, M12, M22 = mass_matrix(arm, q2)
    h = coupling(arm, q2)
    g1, g2 = gravity(arm, q1, q2)
    b1 = tau1 + h * (2 * w1 * w2 + w2**2) - g1
    b2 = tau2 - h * w1**2 - g2
    det = M11 * M22 - M12**2
    return (M22 * b1 - M12 * b2) / det, (M11 * b2 - M12 * b1) / det


def forward_dynamics(arm: ArmModel, t, tau1, tau2, x0, rtol=1e-10):
    def rhs(time, x):
        a1, a2 = accelerations(arm, x, np.interp(time, t, tau1), np.interp(time, t, tau2))
        return [x[2], x[3], a1, a2]

    return solve_ivp(rhs, (t[0], t[-1]), x0, t_eval=t, rtol=rtol, atol=1e-12, max_step=t[1] - t[0])


def mechanical_energy(arm: ArmModel, x):
    q1, q2, w1, w2 = x
    M11, M12, M22 = mass_matrix(arm, q2)
    kinetic = 0.5 * (M11 * w1**2 + 2 * M12 * w1 * w2 + M22 * w2**2)
    potential = -G * ((arm.m1 * arm.c1 + arm.m2 * arm.L1) * np.cos(q1) + arm.m2 * arm.c2 * np.cos(q1 + q2))
    return kinetic + potential


def point_accelerations(L1: float, traj: Trajectory, positions):
    q1, phi = traj.shoulder, traj.forearm_angle
    elbow = L1 * (q1.qdd * np.stack([np.cos(q1.q), np.sin(q1.q)])
                  + q1.qd**2 * np.stack([-np.sin(q1.q), np.cos(q1.q)]))
    normal = np.stack([np.cos(phi.q), np.sin(phi.q)])
    axis_dd = phi.qdd * normal + phi.qd**2 * np.stack([-np.sin(phi.q), np.cos(phi.q)])
    return [elbow + x * axis_dd for x in positions]


def newton_euler_moment(L1: float, traj: Trajectory, bodies: list[PointBody], pivot: float = 0.0):
    phi = traj.forearm_angle
    axis = np.stack([np.sin(phi.q), -np.cos(phi.q)])
    g_vec = np.array([0.0, -G])[:, None]
    force = np.zeros_like(axis)
    moment = np.zeros_like(phi.q)
    for body, acc in zip(bodies, point_accelerations(L1, traj, [b.position for b in bodies])):
        f = body.mass * (acc - g_vec)
        force += f
        moment += (body.position - pivot) * (axis[0] * f[1] - axis[1] * f[0]) + body.inertia * phi.qdd
    return force, moment
