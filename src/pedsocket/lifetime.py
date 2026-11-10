from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .body import body_at
from .config import Params
from .growth import Child
from .interface import WorstCase, worst_case
from .prosthesis import design_socket, strain_for_pressure

MAX_AGE = 20.0


# The loosest fit that still keeps the prosthesis on: friction x fit pressure x contact area has to beat the worst
# pull-out force by the safety factor (1.25). This is the "growth allowance" fit.
def min_fit_strain(child: Child, fit_age: float, p: Params) -> float:
    w = worst_case(child, design_socket(child, fit_age, p), fit_age, p)
    needed = p.suspension_safety * w.pull_out / (p.friction * w.state.contact_area)
    return float(strain_for_pressure(needed, p))


@dataclass(frozen=True)
class Lifetime:
    fit_age: float
    fit_strain: float
    years: float
    at_failure: WorstCase | None

    @property
    def months(self) -> float:
        return 12.0 * self.years

    @property
    def outlasts_growth(self) -> bool:
        return not np.isfinite(self.years)

    @property
    def cause(self) -> str:
        if self.at_failure is None:
            return "none"
        return "pressure" if self.at_failure.stress_index > 1.0 else "suspension"


def socket_lifetime(child: Child, fit_age: float, p: Params, fit_strain: float | None = None,
                    horizon: float = 8.0, step: float = 1 / 12, refinements: int = 10) -> Lifetime:
    socket = design_socket(child, fit_age, p, fit_strain)
    check = lambda age: worst_case(child, socket, age, p)
    end = min(fit_age + horizon, MAX_AGE)
    previous, age = fit_age, fit_age
    while age <= end + 1e-9:
        w = check(age)
        if w.failed:
            if age == fit_age:
                return Lifetime(fit_age, socket.fit_strain, 0.0, w)
            lo, hi = previous, age
            for _ in range(refinements):
                mid = 0.5 * (lo + hi)
                lo, hi = (lo, mid) if check(mid).failed else (mid, hi)
            return Lifetime(fit_age, socket.fit_strain, hi - fit_age, check(hi))
        previous, age = age, age + step
    return Lifetime(fit_age, socket.fit_strain, np.nan, None)


def replacement_schedule(child: Child, start: float, end: float, p: Params, policy: str = "standard") -> list[Lifetime]:
    sockets, age = [], start
    while age < end:
        strain = p.fit_strain if policy == "standard" else min_fit_strain(child, age, p)
        life = socket_lifetime(child, age, p, strain, horizon=end - age + 1e-6)
        sockets.append(life)
        if life.outlasts_growth or life.years <= 1e-6:
            break
        age += life.years
    return sockets


# Spare capacity of a brand-new, loosely fitted socket: 1 means no load at all, 0 means it is right at the tolerance.
def fresh_socket_margin(child: Child, age: float, p: Params) -> float:
    socket = design_socket(child, age, p, min_fit_strain(child, age, p))
    return 1.0 - worst_case(child, socket, age, p).stress_index


def limb_grows_by_rule(child: Child, p: Params, reference_age: float):
    """Sensitivity helper: return a function age -> Params in which the residual limb really does follow the growth rule.

    The baseline gives every new socket a limb that is `residual_fraction` of the current forearm. Here the limb is that
    fraction of the forearm only at `reference_age`, and afterwards grows at `proximal_growth_share` of the forearm's growth.
    """
    f_ref = body_at(child, reference_age, p).forearm_length

    def params_at(age: float) -> Params:
        if age <= reference_age:
            return p
        f_now = body_at(child, age, p).forearm_length
        residual = p.residual_fraction * f_ref + p.proximal_growth_share * (f_now - f_ref)
        return p.updated(residual_fraction=residual / f_now)

    return params_at


# The age at which a brand-new socket first has no margin left. `params_at` is optional and lets a sensitivity run change an
# assumption with age (leave it out for the baseline).
def window_closure_age(child: Child, p: Params, start: float = 4.0, end: float = 18.0, params_at=None) -> float:
    at = params_at or (lambda age: p)
    ages = np.arange(start, end + 1e-9, 0.25)
    margins = [fresh_socket_margin(child, a, at(a)) for a in ages]
    if margins[0] <= 0:
        return float(ages[0])
    for i in range(1, len(ages)):
        if margins[i - 1] > 0 >= margins[i]:
            lo, hi = ages[i - 1], ages[i]
            for _ in range(12):
                mid = 0.5 * (lo + hi)
                lo, hi = (mid, hi) if fresh_socket_margin(child, mid, at(mid)) > 0 else (lo, mid)
            return float(hi)
    return np.nan
