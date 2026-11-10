from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator
from scipy.optimize import least_squares

from .config import DATA_DIR

SEX_CODE = {"boy": 1, "girl": 2}
AGE_WINDOW = (4.0, 20.0)


@lru_cache(maxsize=None)
def lms_table(table: str, sex: str) -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "raw" / f"{table}.csv")
    df = df[df["sex"] == SEX_CODE[sex]].sort_values("agemos").reset_index(drop=True)
    df["age"] = df["agemos"] / 12.0
    return df


# The CDC tables describe each age with three numbers (L, M, S). z = 0 gives the median child and
# z = +/-1.2816 gives the 90th / 10th centile. Same formula the CDC uses.
def lms_quantile(L, M, S, z):
    L, M, S = map(np.asarray, (L, M, S))
    small = np.abs(L) < 1e-8
    safe_L = np.where(small, 1.0, L)
    return np.where(small, M * np.exp(S * z), M * (1.0 + safe_L * S * z) ** (1.0 / safe_L))


def centile_curve(table: str, sex: str, z: float = 0.0, window=AGE_WINDOW):
    df = lms_table(table, sex)
    df = df[(df["age"] >= window[0] - 0.05) & (df["age"] <= window[1] + 0.05)]
    return df["age"].to_numpy(), lms_quantile(df["L"], df["M"], df["S"], z)


# Preece-Baines model 1, closed form. Child.__init__ also solves it as an ODE (dH/dt = s(t)(h1 - H));
# it is the same curve written two ways, and tests/test_growth.py checks they agree.
def preece_baines(t, h1, h_theta, s0, s1, theta):
    tau = np.asarray(t) - theta
    return h1 - 2.0 * (h1 - h_theta) / (np.exp(s0 * tau) + np.exp(s1 * tau))


def preece_baines_rate(t, s0, s1, theta):
    tau = np.asarray(t) - theta
    a, b = np.exp(s0 * tau), np.exp(s1 * tau)
    return (s0 * a + s1 * b) / (a + b)


def fit_preece_baines(ages, heights, theta_guess):
    x0 = [heights[-1], heights[-1] - 12.0, 0.1, 1.2, theta_guess]
    lower = [heights[-1] - 10, 100.0, 0.01, 0.3, 8.0]
    upper = [heights[-1] + 10, heights[-1], 0.5, 3.0, 17.0]
    fit = least_squares(lambda p: preece_baines(ages, *p) - heights, x0, bounds=(lower, upper))
    rmse = float(np.sqrt(np.mean(fit.fun**2)))
    return fit.x, rmse


# One simulated child. Heads-up: height and weight use the same z-score, so the "90th centile child" is
# both tall and heavy. Real children vary in height and weight separately.
class Child:
    def __init__(self, sex: str = "boy", z_height: float = 0.0, z_weight: float | None = None):
        self.sex = sex
        self.z_height = z_height
        self.z_weight = z_height if z_weight is None else z_weight
        ages, heights_cm = centile_curve("statage", sex, z_height)
        self.data_ages, self.data_heights_cm = ages, heights_cm
        self.pb, self.pb_rmse_cm = fit_preece_baines(ages, heights_cm, 13.5 if sex == "boy" else 11.5)
        h1, _, s0, s1, theta = self.pb
        t0, t1 = AGE_WINDOW
        self._height_solution = solve_ivp(
            lambda t, h: preece_baines_rate(t, s0, s1, theta) * (h1 - h),
            (t0, t1), [preece_baines(t0, *self.pb)],
            dense_output=True, rtol=1e-10, atol=1e-10,
        )
        weight_ages, weights = centile_curve("wtage", sex, self.z_weight)
        self._weight = PchipInterpolator(weight_ages, weights)

    @property
    def label(self) -> str:
        if self.z_height == 0:
            return f"{self.sex}, 50th centile"
        from scipy.stats import norm
        return f"{self.sex}, {100 * norm.cdf(self.z_height):.0f}th centile"

    def height(self, age):
        return self._height_solution.sol(np.atleast_1d(age))[0] / 100.0

    def growth_velocity(self, age):
        h1, _, s0, s1, theta = self.pb
        return preece_baines_rate(np.atleast_1d(age), s0, s1, theta) * (h1 - 100.0 * self.height(age)) / 100.0

    def mass(self, age):
        return self._weight(np.atleast_1d(age))

    def mass_rate(self, age):
        """dM/dt in kg per year (derivative of the monotone cubic through the CDC weight centile)."""
        return self._weight.derivative()(np.atleast_1d(age))

    def peak_height_velocity(self):
        ages = np.linspace(8.0, 18.0, 2001)
        v = self.growth_velocity(ages)
        i = int(np.argmax(v))
        return float(ages[i]), float(100.0 * v[i])
