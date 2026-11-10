import numpy as np
import pytest

from pedsocket import design_socket, interface_state
from pedsocket.analytic import static_hold_pressure
from pedsocket.interface import edge_line_loads, socket_loads


def test_line_load_satisfies_force_and_moment_balance():
    shear, moment, length = 8.0, 1.5, 0.08
    q0, qL = edge_line_loads(shear, moment, length)
    z = np.linspace(0, length, 200001)
    q = q0 + (qL - q0) * z / length
    assert np.isclose(np.trapezoid(q, z), shear, rtol=1e-8)
    assert np.isclose(np.trapezoid(q * z, z), moment, rtol=1e-8)


def test_static_hold_matches_closed_form(boy, socket8, params):
    loads = socket_loads(params.task("Static hold"), boy, socket8, 8.0, params)
    assert np.allclose(loads.moment_pressure, static_hold_pressure(socket8, 8.0, boy, params), rtol=1e-10)


def test_fit_strain_is_built_into_new_socket(boy, socket8, params):
    assert np.isclose(interface_state(boy, socket8, 8.0, params).tissue_strain, params.fit_strain)


def test_tapered_socket_seats_fully_when_new(boy, params):
    tapered = params.updated(socket_shape="tapered")
    state = interface_state(boy, design_socket(boy, 8.0, tapered), 8.0, tapered)
    assert state.ride_up == 0.0


def test_tapered_socket_rides_up_as_limb_grows(boy, params):
    tapered = params.updated(socket_shape="tapered")
    socket = design_socket(boy, 8.0, tapered)
    rides = [interface_state(boy, socket, a, tapered).ride_up for a in (8.5, 9.0, 9.5)]
    assert 0 < rides[0] < rides[1] < rides[2]


@pytest.mark.parametrize("age", [9.0, 10.0])
def test_growth_tightens_cylindrical_socket(boy, socket8, params, age):
    assert interface_state(boy, socket8, age, params).fit_pressure > interface_state(boy, socket8, 8.0, params).fit_pressure
