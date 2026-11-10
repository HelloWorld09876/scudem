from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .body import Body
from .config import Params
from .dynamics import G, build_arm, intact_forearm, inverse_dynamics, prosthetic_side, residual_limb
from .growth import Child
from .kinematics import trajectory
from .prosthesis import Socket, interface_state


def strength(body: Body, p: Params) -> tuple[float, float]:
    scale = (body.mass / p.reference_mass) ** (2 / 3) * (body.height / p.reference_height)
    return p.elbow_strength_adult * scale, p.shoulder_strength_adult * scale


@dataclass(frozen=True)
class Musculoskeletal:
    age: float
    reach_deficit: float
    trunk_lean_deg: float
    lumbar_moment_pct: float
    elbow_effort_prosthetic: float
    elbow_effort_intact: float
    shoulder_effort_prosthetic: float
    shoulder_effort_intact: float


def musculoskeletal(child: Child, socket: Socket, age: float, p: Params) -> Musculoskeletal:
    state = interface_state(child, socket, age, p)
    b = state.body
    elbow_max, shoulder_max = strength(b, p)
    prosthetic_arm = build_arm(b, [residual_limb(state, p)] + prosthetic_side(socket, state, p), p)
    intact_arm = build_arm(b, intact_forearm(b, p), p)
    efforts = np.zeros(4)
    for task in p.tasks:
        traj = trajectory(task, p, 121)
        s_p, e_p = inverse_dynamics(prosthetic_arm, traj)
        s_i, e_i = inverse_dynamics(intact_arm, traj)
        current = [np.abs(e_p).max() / (p.residual_strength_ratio * elbow_max), np.abs(e_i).max() / elbow_max,
                   np.abs(s_p).max() / shoulder_max, np.abs(s_i).max() / shoulder_max]
        efforts = np.maximum(efforts, current)
    # The prosthesis is cut to the intact arm's length on fitting day and then stays that length, so the gap opens up as
    # the other arm grows (clinicians call this prosthetic length discrepancy).
    deficit = b.grip_distance - state.grip_distance
    trunk = p.f_trunk_length * b.height
    # Simplest possible compensation: lean the trunk forward until the hand reaches the same place. A rough trend, not a prediction.
    lean = float(np.degrees(np.arcsin(np.clip(deficit / trunk, 0.0, 1.0))))
    lumbar = p.f_hat_mass * b.mass * G * p.hat_com * trunk * np.sin(np.radians(lean))
    return Musculoskeletal(age, deficit, lean, 100 * lumbar / (b.mass * G * b.height), *efforts)
