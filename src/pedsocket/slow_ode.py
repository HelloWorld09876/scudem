"""The slow (growth) system written as an initial-value problem, with failure as an event.

For a frozen cylindrical socket fitted at age t_f the interface evolves as

    dH/dt   = s(t) (h1 - H)                          Preece-Baines growth of height          (cm / yr)
    dl/dt   = phi f_f dH/dt                          residual limb lengthens at a share phi of forearm growth
    dr/dt   = (r/2) (M'/M - H'/H)                    girth follows r ~ sqrt(M/H); M(t) is the CDC weight centile
    de/dt   = (1/beta - e) (r'/r)                    tissue strain, from e = (r - r_s)/(beta r) with the socket radius r_s fixed
    dp/dt   = (E + B p) de/dt                        exponential tissue law p = (E/B)(exp(B e) - 1) differentiated

and the socket is replaced at the first event

    p_fit(t) + p_lift(t) = p_tol            (pressure),        mu p_fit A_contact(t) = pull-out force(t)      (suspension).

p_lift(t) is the peak lifting pressure of the fast system (two-link arm, 0.5-1.2 s per action). Arm motion is about 10^8 times faster
than growth, so the growth system sees only the peak of the fast response, which is computed from the Lagrange model at the
current body state (a quasi-steady, two-time-scale reduction).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.integrate import solve_ivp

from .body import body_at
from .config import Params
from .growth import Child, preece_baines_rate
from .interface import worst_case
from .prosthesis import design_socket, strain_for_pressure, tissue_pressure

SECONDS_PER_YEAR = 365.25 * 24 * 3600


def slow_rhs(t, y, child: Child, p: Params):
    height, _, radius, strain, fit_pressure = y
    h1, _, s0, s1, theta = child.pb
    height_rate = preece_baines_rate(t, s0, s1, theta) * (h1 - height)
    mass = float(child.mass(t)[0])
    log_radius_rate = 0.5 * (float(child.mass_rate(t)[0]) / mass - height_rate / height)
    strain_rate = (1.0 / p.soft_tissue_fraction - strain) * log_radius_rate
    return [height_rate, p.proximal_growth_share * p.f_forearm_length * height_rate / 100.0,
            radius * log_radius_rate, strain_rate, (p.tissue_modulus + p.tissue_stiffening * fit_pressure) * strain_rate]


@dataclass(frozen=True)
class SlowResult:
    fit_age: float
    t: np.ndarray                 # age (years)
    y: np.ndarray                 # rows: H (cm), residual length (m), radius (m), strain, fit pressure (Pa)
    lift: np.ndarray              # lifting pressure p_lift(t) from the fast system (Pa)
    event: str | None             # "pressure", "suspension" or None
    event_age: float | None

    @property
    def months(self) -> float:
        return float("nan") if self.event_age is None else 12.0 * (self.event_age - self.fit_age)


def integrate_socket(child: Child, fit_age: float, p: Params, fit_strain: float | None = None,
                     horizon: float = 8.0, n_out: int = 241, rtol: float = 1e-9) -> SlowResult:
    """Integrate the slow system from the fitting day until the first failure event (cylindrical sockets)."""
    if p.socket_shape != "cylindrical":
        raise ValueError("the tapered socket adds an algebraic seating constraint; use lifetime.socket_lifetime for it")
    socket = design_socket(child, fit_age, p, fit_strain)
    b0 = body_at(child, fit_age, p)
    y0 = [100.0 * b0.height, socket.residual_length_at_fit, b0.residual_radius, socket.fit_strain,
          float(tissue_pressure(socket.fit_strain, p))]

    cache: dict[float, tuple] = {}

    def fast(t):                   # peak lifting pressure and pull-out force of the fast system at body state t
        if t not in cache:
            w = worst_case(child, socket, t, p)
            cache[t] = (w.peak_pressure - w.state.fit_pressure, w.pull_out)
        return cache[t]

    def pressure_event(t, y):
        return y[4] + fast(t)[0] - p.pressure_tolerance

    def suspension_event(t, y):
        engaged = y[1] - max(0.0, y[1] - socket.depth)
        return p.friction * y[4] * 2.0 * np.pi * y[2] * engaged / max(fast(t)[1], 1e-12) - 1.0

    pressure_event.terminal, pressure_event.direction = True, +1
    suspension_event.terminal, suspension_event.direction = True, -1

    end = min(fit_age + horizon, 20.0)
    if pressure_event(fit_age, y0) >= 0 or suspension_event(fit_age, y0) <= 0:      # already failed on the fitting day
        return SlowResult(fit_age, np.array([fit_age]), np.array(y0)[:, None], np.array([fast(fit_age)[0]]),
                          "pressure" if pressure_event(fit_age, y0) >= 0 else "suspension", fit_age)
    sol = solve_ivp(lambda t, y: slow_rhs(t, y, child, p), (fit_age, end), y0, method="DOP853", rtol=rtol, atol=1e-12,
                    events=[pressure_event, suspension_event], dense_output=True)
    which = next((name for name, ev in zip(("pressure", "suspension"), sol.t_events) if len(ev)), None)
    event_age = float(sol.t_events[0][0] if which == "pressure" else sol.t_events[1][0]) if which else None
    t_end = event_age if event_age is not None else end
    t = np.linspace(fit_age, t_end, n_out)
    y = sol.sol(t)
    return SlowResult(fit_age, t, y, np.array([fast(float(x))[0] for x in t]), which, event_age)


def girth_budget(p: Params, fit_strain: float, lift_pressure: float) -> float:
    """Closed form: radius ratio r*/r0 at which a socket made for `fit_strain` reaches the pressure tolerance.

    From (1 - beta e) = (1 - beta e0) r0 / r, with e* the strain whose tissue pressure is p_tol - p_lift."""
    e_star = float(strain_for_pressure(p.pressure_tolerance - lift_pressure, p))
    beta = p.soft_tissue_fraction
    return (1.0 - beta * fit_strain) / (1.0 - beta * e_star)
