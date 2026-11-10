import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation

from common import BASE, BOY, FIT_AGE
from pedsocket import design_socket
from pedsocket.config import FIGURE_DIR
from pedsocket.interface import socket_loads

socket = design_socket(BOY, FIT_AGE, BASE)
cmap = plt.get_cmap("RdYlGn_r")


def render(task_name: str, filename: str):
    r = socket_loads(BASE.task(task_name), BOY, socket, FIT_AGE, BASE, n=72)
    L1 = r.state.body.upper_arm_length
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set(xlim=(-0.15, 0.55), ylim=(-0.5, 0.5), aspect="equal")
    ax.axis("off")
    ax.plot(0, 0, "ko", ms=10)
    upper, = ax.plot([], [], color="#9ca3af", lw=7, solid_capstyle="round")
    sock, = ax.plot([], [], lw=11, solid_capstyle="butt")
    pros, = ax.plot([], [], color="#1f5fa8", lw=5)
    obj, = ax.plot([], [], "ks", ms=11)
    label = ax.text(-0.13, 0.43, "", fontsize=11, family="monospace")
    ax.set_title(f"{task_name}: socket pressure", fontsize=12)

    def frame(i):
        a1, phi = r.traj.shoulder.q[i], r.traj.forearm_angle.q[i]
        elbow = L1 * np.array([np.sin(a1), -np.cos(a1)])
        axis = np.array([np.sin(phi), -np.cos(phi)])
        brim, hand = elbow + r.state.engaged_length * axis, elbow + r.state.grip_distance * axis
        upper.set_data([0, elbow[0]], [0, elbow[1]])
        sock.set_data([elbow[0], brim[0]], [elbow[1], brim[1]])
        sock.set_color(cmap(min(r.peak_pressure[i] / BASE.pressure_tolerance, 1.0)))
        pros.set_data([brim[0], hand[0]], [brim[1], hand[1]])
        obj.set_data([hand[0]], [hand[1]])
        label.set_text(f"{r.peak_pressure[i] / 1e3:5.1f} kPa")
        return upper, sock, pros, obj, label

    anim = animation.FuncAnimation(fig, frame, frames=len(r.traj.t), blit=True)
    anim.save(FIGURE_DIR / filename, writer=animation.PillowWriter(fps=24))
    plt.close(fig)
    print(f"  figures/{filename}")


render("Lift to shelf", "anim_lift_to_shelf.gif")
render("Fast curl", "anim_fast_curl.gif")
