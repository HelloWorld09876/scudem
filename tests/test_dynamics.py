import numpy as np
import pytest

from pedsocket import body_at, interface_state
from pedsocket.dynamics import (build_arm, forward_dynamics, intact_forearm, inverse_dynamics, mechanical_energy,
                                newton_euler_moment, prosthetic_side, residual_limb)
from pedsocket.kinematics import MIN_JERK_PEAK_ACCEL, min_jerk, trajectory


@pytest.fixture
def intact_arm(boy, params):
    b = body_at(boy, 10.0, params)
    return b, intact_forearm(b, params), build_arm(b, intact_forearm(b, params), params)


def test_passive_arm_conserves_energy(intact_arm):
    _, _, arm = intact_arm
    t = np.linspace(0.0, 2.0, 2001)
    zero = np.zeros_like(t)
    sol = forward_dynamics(arm, t, zero, zero, [0.6, 0.9, 0.0, 0.0], rtol=1e-11)
    energy = mechanical_energy(arm, sol.y)
    assert np.max(np.abs(energy - energy[0])) / abs(energy[0]) < 1e-6


@pytest.mark.parametrize("task_index", range(4))
def test_lagrange_matches_newton_euler_at_elbow(intact_arm, params, task_index):
    _, forearm, arm = intact_arm
    traj = trajectory(params.tasks[task_index], params)
    _, tau_elbow = inverse_dynamics(arm, traj)
    _, moment = newton_euler_moment(arm.L1, traj, forearm, pivot=0.0)
    assert np.allclose(tau_elbow, moment, rtol=1e-9, atol=1e-9)


def test_forward_integration_reproduces_motion(boy, socket8, params):
    state = interface_state(boy, socket8, 8.0, params)
    arm = build_arm(state.body, [residual_limb(state, params)] + prosthetic_side(socket8, state, params), params)
    traj = trajectory(params.task("Lift to shelf"), params, 401)
    tau1, tau2 = inverse_dynamics(arm, traj)
    x0 = [traj.shoulder.q[0], traj.elbow.q[0], traj.shoulder.qd[0], traj.elbow.qd[0]]
    sol = forward_dynamics(arm, traj.t, tau1, tau2, x0)
    assert np.degrees(np.max(np.abs(sol.y[1] - traj.elbow.q))) < 0.05


def test_min_jerk_peak_acceleration():
    t = np.linspace(0, 1, 200001)
    path = min_jerk(0.0, 1.0, 1.0, t)
    assert abs(path.qdd.max() - MIN_JERK_PEAK_ACCEL) < 1e-6
