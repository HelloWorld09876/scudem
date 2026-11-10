from __future__ import annotations

import tomllib
from dataclasses import dataclass, fields, replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data"
FIGURE_DIR = ROOT / "figures"
RESULT_DIR = ROOT / "results"


@dataclass(frozen=True)
class Task:
    name: str
    shoulder_deg: tuple[float, float]
    elbow_deg: tuple[float, float]
    duration: float


@dataclass(frozen=True)
class Params:
    f_upper_arm_length: float
    f_forearm_length: float
    f_hand_length: float
    f_upper_arm_mass: float
    f_forearm_mass: float
    f_hand_mass: float
    upper_arm_com: float
    upper_arm_gyration: float
    forearm_com: float
    forearm_gyration: float
    tissue_density: float
    residual_fraction: float
    proximal_growth_share: float
    atrophy_ratio: float
    soft_tissue_fraction: float
    tissue_modulus: float
    tissue_stiffening: float
    friction: float
    pressure_tolerance: float
    prosthesis_mass: float
    prosthesis_com: float
    prosthesis_gyration: float
    distal_clearance: float
    fit_strain: float
    suspension_safety: float
    socket_shape: str
    taper_deg: float
    donning_force: float
    load_mode: str
    object_mass: float
    object_fraction: float
    speed_factor: float
    elbow_strength_adult: float
    shoulder_strength_adult: float
    residual_strength_ratio: float
    reference_mass: float
    reference_height: float
    f_trunk_length: float
    f_hat_mass: float
    hat_com: float
    interface_damping: float
    tasks: tuple[Task, ...]

    def updated(self, **changes) -> "Params":
        return replace(self, **changes)

    def scaled(self, name: str, factor: float) -> "Params":
        return replace(self, **{name: getattr(self, name) * factor})

    def task(self, name: str) -> Task:
        return next(t for t in self.tasks if t.name == name)


def load_params(path: str | Path = CONFIG_DIR / "baseline.toml", **overrides) -> Params:
    raw = tomllib.loads(Path(path).read_text())
    tasks = tuple(
        Task(t["name"], tuple(t["shoulder_deg"]), tuple(t["elbow_deg"]), float(t["duration"]))
        for t in raw.pop("tasks")
    )
    flat = {key: value for section in raw.values() for key, value in section.items()}
    expected = {f.name for f in fields(Params)} - {"tasks"}
    missing, unknown = expected - flat.keys(), flat.keys() - expected
    if missing or unknown:
        raise KeyError(f"config mismatch: missing={sorted(missing)} unknown={sorted(unknown)}")
    return Params(**flat, tasks=tasks).updated(**overrides)
