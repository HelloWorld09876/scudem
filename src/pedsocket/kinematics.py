from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import Params, Task

# Peak acceleration of a minimum-jerk move is (10/sqrt(3)) * distance / T^2.
MIN_JERK_PEAK_ACCEL = 10.0 / np.sqrt(3.0)


@dataclass(frozen=True)
class JointPath:
    q: np.ndarray
    qd: np.ndarray
    qdd: np.ndarray


@dataclass(frozen=True)
class Trajectory:
    t: np.ndarray
    shoulder: JointPath
    elbow: JointPath

    @property
    def forearm_angle(self) -> JointPath:
        return JointPath(self.shoulder.q + self.elbow.q, self.shoulder.qd + self.elbow.qd,
                         self.shoulder.qdd + self.elbow.qdd)


def min_jerk(q0: float, qf: float, duration: float, t: np.ndarray) -> JointPath:
    tau = np.clip(t / duration, 0.0, 1.0)
    d = qf - q0
    return JointPath(
        q0 + d * (10 * tau**3 - 15 * tau**4 + 6 * tau**5),
        d * (30 * tau**2 - 60 * tau**3 + 30 * tau**4) / duration,
        d * (60 * tau - 180 * tau**2 + 120 * tau**3) / duration**2,
    )


def task_duration(task: Task, p: Params) -> float:
    return task.duration / p.speed_factor


def trajectory(task: Task, p: Params, n: int = 201) -> Trajectory:
    duration = task_duration(task, p)
    t = np.linspace(0.0, duration, n)
    return Trajectory(
        t,
        min_jerk(*np.radians(task.shoulder_deg), duration, t),
        min_jerk(*np.radians(task.elbow_deg), duration, t),
    )


# Pi: roughly the inertial moment divided by the gravity moment during a move. Big Pi means the move is fast for the lever length.
def dynamic_number(task: Task, p: Params, lever: float, g: float = 9.81) -> float:
    sweep = np.radians(abs(task.elbow_deg[1] - task.elbow_deg[0]) + abs(task.shoulder_deg[1] - task.shoulder_deg[0]))
    return MIN_JERK_PEAK_ACCEL * sweep * lever / (g * task_duration(task, p) ** 2)
