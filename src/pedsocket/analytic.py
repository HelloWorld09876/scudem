from __future__ import annotations

import numpy as np

from .config import Params
from .dynamics import G, object_mass
from .growth import Child
from .prosthesis import Socket, design_socket, interface_state


# Model 0, the case you can solve by hand: the child holds the object still with the elbow at 90 degrees, so the load on
# the socket is just weights times lever arms (V and M_B in the paper).
def static_hold_loads(socket: Socket, age: float, child: Child, p: Params):
    state = interface_state(child, socket, age, p)
    m_p, m_o = p.prosthesis_mass, object_mass(state.body, p)
    x_p = p.prosthesis_com * socket.prosthesis_length
    shear = G * (m_p + m_o)
    moment = G * (m_p * x_p + m_o * socket.prosthesis_length)
    return state, shear, moment


# Edge loads from force and moment balance with a linear line load (paper eq. 4), then peak pressure over half the circumference (eq. 5).
def static_hold_pressure(socket: Socket, age: float, child: Child, p: Params) -> float:
    state, shear, moment = static_hold_loads(socket, age, child, p)
    L, r = state.engaged_length, state.radius
    proximal = 4 * shear / L - 6 * moment / L**2
    distal = -2 * shear / L + 6 * moment / L**2
    return 2 * max(abs(proximal), abs(distal)) / (np.pi * r)


def leading_order_pressure(socket: Socket, age: float, child: Child, p: Params) -> float:
    state, _, moment = static_hold_loads(socket, age, child, p)
    return 12 * moment / (np.pi * state.radius * state.engaged_length**2)


def fresh_socket_static_pressure(child: Child, age: float, p: Params) -> float:
    return static_hold_pressure(design_socket(child, age, p), age, child, p)


def power_law(x, y):
    slope, intercept = np.polyfit(np.log(x), np.log(y), 1)
    return slope, np.exp(intercept)
