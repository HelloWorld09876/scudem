import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pedsocket import Child, load_params
from pedsocket.plotting import use_style

use_style()

FIT_AGE = 8.0
BASE = load_params()
TAPERED = BASE.updated(socket_shape="tapered")
GROWING = BASE.updated(load_mode="scaled")
BOY, GIRL = Child("boy"), Child("girl")
CHILDREN = (BOY, GIRL)
CENTILES = {"10th": -1.2816, "50th": 0.0, "90th": 1.2816}
