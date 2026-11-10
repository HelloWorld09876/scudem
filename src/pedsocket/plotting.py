from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .config import FIGURE_DIR, RESULT_DIR

BOY, GIRL = "#1f5fa8", "#c2410c"
TASK_COLORS = {"Static hold": "#4b5563", "Slow curl": "#1f5fa8", "Fast curl": "#c2410c", "Lift to shelf": "#15803d"}
LIFT, GROWTH, LIMIT = "#93c5fd", "#fdba74", "#dc2626"


def use_style():
    plt.rcParams.update({
        "font.size": 11, "axes.titlesize": 12, "axes.grid": True, "grid.alpha": 0.25,
        "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
        "figure.dpi": 110, "savefig.dpi": 220, "savefig.bbox": "tight", "figure.constrained_layout.use": True,
    })


def sex_color(sex: str) -> str:
    return BOY if sex == "boy" else GIRL


def save(fig, name: str):
    FIGURE_DIR.mkdir(exist_ok=True)
    fig.savefig(FIGURE_DIR / f"{name}.png")
    plt.close(fig)
    print(f"  figures/{name}.png")


def record(step: str, values: dict):
    RESULT_DIR.mkdir(exist_ok=True)
    path = RESULT_DIR / f"{step}.json"
    path.write_text(json.dumps(values, indent=2, default=float))
    print(f"  results/{step}.json")
