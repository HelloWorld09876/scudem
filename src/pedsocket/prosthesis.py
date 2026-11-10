from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import brentq

from .body import Body, body_at
from .config import Params
from .growth import Child


# Soft tissue gets stiffer the more it is squeezed: p = (E/B)(exp(B*strain) - 1), the exponential form used by Fung (1993).
# The values of E and B in the config are working assumptions, not measurements on children.
def tissue_pressure(strain, p: Params):
    strain = np.maximum(strain, 0.0)
    return p.tissue_modulus / p.tissue_stiffening * np.expm1(p.tissue_stiffening * strain)


def strain_for_pressure(pressure, p: Params):
    return np.log1p(np.maximum(pressure, 0.0) * p.tissue_stiffening / p.tissue_modulus) / p.tissue_stiffening


@dataclass(frozen=True)
class Socket:
    fit_age: float
    fit_strain: float
    residual_length_at_fit: float
    forearm_length_at_fit: float
    depth: float
    radius: float
    prosthesis_length: float


@dataclass(frozen=True)
class InterfaceState:
    body: Body
    residual_length: float
    offset: float
    ride_up: float
    engaged_length: float
    radius: float
    tissue_strain: float
    fit_pressure: float
    grip_distance: float

    @property
    def contact_area(self) -> float:
        return 2.0 * np.pi * self.radius * self.engaged_length


# A socket is made for the limb as it is on fitting day. Note that the residual limb is taken as a fixed share
# (residual_fraction) of the forearm at the fitting age, for every fitting age. So a brand-new socket at 14 sees a
# limb that is 45% of a 14-year-old's forearm, even though the model also says the limb grows slower than the forearm.
# scripts/11_closure_sensitivity.py shows how much that matters for the window-closure age.
def design_socket(child: Child, fit_age: float, p: Params, fit_strain: float | None = None) -> Socket:
    b = body_at(child, fit_age, p)
    strain = p.fit_strain if fit_strain is None else fit_strain
    residual = p.residual_fraction * b.forearm_length
    radius = b.residual_radius * (1.0 - strain * p.soft_tissue_fraction)
    return Socket(
        fit_age=fit_age,
        fit_strain=strain,
        residual_length_at_fit=residual,
        forearm_length_at_fit=b.forearm_length,
        depth=residual + p.distal_clearance,
        radius=radius,
        prosthesis_length=b.grip_distance,
    )


# Tapered socket: how much pressure the child can overcome when pushing the limb in (donning force spread over the
# wall area, plus a wedge term from friction and the taper angle).
def donning_pressure(radius: float, engaged: float, p: Params) -> float:
    alpha = np.radians(p.taper_deg)
    wedge = p.friction * np.cos(alpha) + np.sin(alpha)
    return p.donning_force / (2.0 * np.pi * radius * engaged * wedge)


# Where does the limb end up sitting in a tapered socket? If the squeeze is more than the donning force can push
# through, the limb stays partly out (ride-up). We find the balance point with Brent's method.
def _seating_offset(radius, interference, residual, bottom_offset, p: Params) -> float:
    if p.socket_shape != "tapered" or interference <= 0.0:
        return bottom_offset
    tan_a = np.tan(np.radians(p.taper_deg))
    thickness = p.soft_tissue_fraction * radius

    def excess(s):
        strain = (interference - s * tan_a) / thickness
        return tissue_pressure(strain, p) - donning_pressure(radius, residual - s, p)

    if excess(bottom_offset) <= 0.0:
        return bottom_offset
    upper = min(interference / tan_a, 0.95 * residual)
    if excess(upper) > 0.0:
        return upper
    return brentq(excess, bottom_offset, upper, xtol=1e-9)


def interface_state(child: Child, socket: Socket, age: float, p: Params) -> InterfaceState:
    b = body_at(child, age, p)
    residual = socket.residual_length_at_fit + p.proximal_growth_share * (b.forearm_length - socket.forearm_length_at_fit)
    bottom_offset = max(0.0, residual - socket.depth)
    radius = b.residual_radius
    interference = radius - socket.radius
    offset = _seating_offset(radius, interference, residual, bottom_offset, p)
    if p.socket_shape == "tapered":
        interference -= offset * np.tan(np.radians(p.taper_deg))
    strain = interference / (p.soft_tissue_fraction * radius)
    return InterfaceState(
        body=b,
        residual_length=residual,
        offset=offset,
        ride_up=offset - bottom_offset,
        engaged_length=residual - offset,
        radius=radius,
        tissue_strain=float(strain),
        fit_pressure=float(tissue_pressure(strain, p)),
        grip_distance=offset + socket.prosthesis_length,
    )
