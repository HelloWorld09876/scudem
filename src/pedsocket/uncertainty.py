from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import qmc, spearmanr

from .config import Params
from .growth import Child
from .interface import worst_case
from .lifetime import min_fit_strain, socket_lifetime, window_closure_age
from .prosthesis import design_socket

# Nine inputs we are unsure about, each sampled over a plausible range. Not sampled here: the load fraction (2% of body
# mass), the action speeds, the donning force, the taper angle and the body proportions. For the load fraction and a few other
# assumptions that matter a lot for the window-closure age, see scripts/11_closure_sensitivity.py.
UNCERTAIN = {
    "tissue_modulus": (50e3, 150e3),
    "tissue_stiffening": (4.0, 8.0),
    "pressure_tolerance": (75e3, 125e3),
    "friction": (0.35, 0.75),
    "prosthesis_mass": (0.30, 0.60),
    "residual_fraction": (0.35, 0.55),
    "soft_tissue_fraction": (0.30, 0.50),
    "atrophy_ratio": (0.80, 1.00),
    "proximal_growth_share": (0.15, 0.30),
}


@dataclass(frozen=True)
class MonteCarlo:
    names: list[str]
    samples: np.ndarray
    initial_index: np.ndarray
    lifetime_standard: np.ndarray
    slips_standard: np.ndarray
    lifetime_individual: np.ndarray
    closure_age: np.ndarray

    @staticmethod
    def interval(values, level=0.9):
        v = values[np.isfinite(values)]
        lo, hi = np.quantile(v, [(1 - level) / 2, (1 + level) / 2])
        return float(np.median(v)), float(lo), float(hi)

    def rank_correlations(self, values):
        ok = np.isfinite(values)
        return {n: float(spearmanr(self.samples[ok, i], values[ok]).statistic) for i, n in enumerate(self.names)}


def latin_hypercube(n: int, seed: int = 26126):
    names = list(UNCERTAIN)
    lower = np.array([UNCERTAIN[k][0] for k in names])
    upper = np.array([UNCERTAIN[k][1] for k in names])
    unit = qmc.LatinHypercube(d=len(names), seed=seed).random(n)
    return names, qmc.scale(unit, lower, upper)


def run_monte_carlo(p_fixed: Params, p_growing: Params, sex: str = "boy", fit_age: float = 8.0,
                    n: int = 400, seed: int = 26126) -> MonteCarlo:
    names, samples = latin_hypercube(n, seed)
    child = Child(sex)
    out = np.full((5, n), np.nan)
    for i, row in enumerate(samples):
        changes = dict(zip(names, row))
        fixed = p_fixed.updated(**changes)
        standard = socket_lifetime(child, fit_age, fixed)
        individual = socket_lifetime(child, fit_age, fixed, min_fit_strain(child, fit_age, fixed))
        out[0, i] = worst_case(child, design_socket(child, fit_age, fixed), fit_age, fixed).stress_index
        out[1, i] = 12 * standard.years
        out[2, i] = float(standard.cause == "suspension")
        out[3, i] = 12 * individual.years
        out[4, i] = window_closure_age(child, p_growing.updated(**changes))
    return MonteCarlo(names, samples, out[0], out[1], out[2].astype(bool), out[3], out[4])
