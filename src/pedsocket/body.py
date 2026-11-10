from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import Params
from .growth import Child


@dataclass(frozen=True)
class Body:
    age: float
    height: float
    mass: float
    upper_arm_length: float
    forearm_length: float
    hand_length: float
    upper_arm_mass: float
    forearm_mass: float
    hand_mass: float
    forearm_radius: float
    residual_radius: float

    @property
    def grip_distance(self) -> float:
        return self.forearm_length + 0.5 * self.hand_length

    @property
    def bmi(self) -> float:
        return self.mass / self.height**2


# Segment lengths and masses are fixed fractions of height and body mass (adult proportions from Winter 2009).
# Young children have relatively bigger heads and shorter limbs, so this is a simplification.
def body_at(child: Child, age: float, p: Params) -> Body:
    height = float(child.height(age)[0])
    mass = float(child.mass(age)[0])
    forearm_length = p.f_forearm_length * height
    forearm_mass = p.f_forearm_mass * mass
    # Forearm as a uniform cylinder of tissue: r = sqrt(m / (pi * rho * length)). Since m scales with M and
    # length with H, the radius grows like sqrt(M/H), so girth follows weight gain relative to height.
    forearm_radius = float(np.sqrt(forearm_mass / (p.tissue_density * np.pi * forearm_length)))
    return Body(
        age=age,
        height=height,
        mass=mass,
        upper_arm_length=p.f_upper_arm_length * height,
        forearm_length=forearm_length,
        hand_length=p.f_hand_length * height,
        upper_arm_mass=p.f_upper_arm_mass * mass,
        forearm_mass=forearm_mass,
        hand_mass=p.f_hand_mass * mass,
        forearm_radius=forearm_radius,
        residual_radius=p.atrophy_ratio * forearm_radius,  # the residual limb is a bit thinner than a full forearm
    )
