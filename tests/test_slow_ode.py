import numpy as np
import pytest

from pedsocket import design_socket, interface_state
from pedsocket.interface import worst_case
from pedsocket.lifetime import min_fit_strain, socket_lifetime
from pedsocket.slow_ode import girth_budget, integrate_socket


def test_mass_rate_matches_finite_difference(boy):
    ages = np.array([6.5, 9.0, 12.0, 15.0])
    h = 1e-4
    fd = (boy.mass(ages + h) - boy.mass(ages - h)) / (2 * h)
    assert np.allclose(boy.mass_rate(ages), fd, rtol=1e-6)


def test_ode_state_matches_algebraic_interface(boy, params):
    res = integrate_socket(boy, 8.0, params)
    socket = design_socket(boy, 8.0, params)
    for k in (0, 60, 120, len(res.t) - 1):
        state = interface_state(boy, socket, float(res.t[k]), params)
        assert res.y[3][k] == pytest.approx(state.tissue_strain, abs=1e-7)
        assert res.y[4][k] == pytest.approx(state.fit_pressure, rel=1e-6)
        assert res.y[2][k] == pytest.approx(state.radius, rel=1e-7)
        assert res.y[1][k] == pytest.approx(state.residual_length, rel=1e-7)


@pytest.mark.parametrize("sex,age", [("boy", 6.0), ("boy", 10.0), ("girl", 8.0), ("girl", 12.0)])
def test_event_time_equals_lifetime_search(sex, age, boy, girl, params):
    child = boy if sex == "boy" else girl
    res = integrate_socket(child, age, params)
    assert res.event == "pressure"
    assert res.months == pytest.approx(socket_lifetime(child, age, params).months, abs=0.01)


def test_patient_specific_fit_event_matches(boy, params):
    strain = min_fit_strain(boy, 8.0, params)
    res = integrate_socket(boy, 8.0, params, strain)
    assert res.months == pytest.approx(socket_lifetime(boy, 8.0, params, strain).months, abs=0.01)


def test_day_one_suspension_failure_fires_at_once(boy, params):
    slip = params.updated(friction=0.12)
    res = integrate_socket(boy, 8.0, slip)
    assert res.event == "suspension" and res.months == pytest.approx(0.0)
    assert socket_lifetime(boy, 8.0, slip).months == pytest.approx(0.0)


def test_girth_and_strain_conserve_one_combination(boy, params):
    # (1 - beta * strain) * radius is constant while the socket radius is fixed.
    res = integrate_socket(boy, 8.0, params)
    invariant = (1 - params.soft_tissue_fraction * res.y[3]) * res.y[2]
    assert np.ptp(invariant) / invariant[0] < 1e-8


def test_girth_budget_closed_form_brackets_the_lifetime(boy, params):
    res = integrate_socket(boy, 8.0, params)
    eps0 = design_socket(boy, 8.0, params).fit_strain
    ratio = res.y[2] / res.y[2][0]
    # at the event the radius ratio equals the budget computed with the lifting pressure at that moment
    assert ratio[-1] == pytest.approx(girth_budget(params, eps0, res.lift[-1]), rel=1e-4)
    assert girth_budget(params, eps0, res.lift[0]) < ratio[-1]


def test_tapered_socket_is_rejected(boy, params):
    with pytest.raises(ValueError):
        integrate_socket(boy, 8.0, params.updated(socket_shape="tapered"))


def test_headroom_path_reproduces_lifetime(boy, params):
    # lifetime for any tolerance = first time the (tolerance-free) peak-pressure path reaches that tolerance
    socket = design_socket(boy, 8.0, params)
    ages = np.arange(8.0, 12.0 + 1e-9, 1 / 48)
    peak = np.array([worst_case(boy, socket, a, params).peak_pressure for a in ages])
    for tol_kpa in (90.0, 110.0, 130.0):
        t_path = 12 * (np.interp(tol_kpa * 1e3, peak, ages) - 8.0)
        t_search = socket_lifetime(boy, 8.0, params.updated(pressure_tolerance=tol_kpa * 1e3)).months
        assert t_path == pytest.approx(t_search, abs=0.05)
