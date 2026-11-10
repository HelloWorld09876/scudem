import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pedsocket import Child, design_socket, load_params


@pytest.fixture(scope="session")
def params():
    return load_params()


@pytest.fixture(scope="session")
def boy():
    return Child("boy")


@pytest.fixture(scope="session")
def girl():
    return Child("girl")


@pytest.fixture(scope="session")
def socket8(boy, params):
    return design_socket(boy, 8.0, params)
