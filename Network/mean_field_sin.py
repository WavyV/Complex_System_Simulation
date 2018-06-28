import networkx as nx
from matplotlib import pyplot as plt
import random
import numpy as np
from matplotlib import animation
from matplotlib import patches


def initialize(N, init_value):
    G = nx.Graph()
    for i in range(N):
        G.add_node(i)
    for i in range(N):
        for j in range(N):
            if i != j:
                G.add_edge(i, j)

    for node in G.nodes():
        G.node[node]['power'] = init_value
    return G


def generate_power(G, a, t, max_power):
    t = t % 1
    if t > 1/2:
        P = 0
    else:
        P = a * np.sin(2 * np.pi * t)
    for node in G.nodes():
        G.node[node]['power'] += P
        if G.node[node]['power'] > max_power:
            G.node[node]['power'] = max_power
        if G.node[node]['power'] < 0:
            G.node[node]['power'] = 0
    return G, P


def use_power(G, c, t):
    # C =  a / np.pi  # Stable situation, overall production = consumption. If < then shortage, if > then buildup of energy stored
    # t = t % 1
    for node in G.nodes():
        G.node[node]['power'] -= c
        if G.node[node]['power'] < 0:
            G.node[node]['power'] = 0
    return G, c


def get_global_status(G):
    total_power = 0
    for node in G.nodes():
        total_power += G.node[node]['power']
    return total_power / len(G.nodes())


def animate_meanfield(N, a, c, init_value, max_power, max_it, dt, jupyter):

    # set dependent variables
    status = np.zeros((max_it, 2))

    G = initialize(N, init_value)

    for t in range(max_it):
        G, C = use_power(G, c, dt*t)
        G, P = generate_power(G, a, dt*t, max_power)
        status[t, 0] = get_global_status(G)
        status[t, 1] = P / C

    # animation
    fig, (ax1, ax2) = plt.subplots(1, 2)

    ax1.set_ylim(-1, max_power+1)
    ax1.set_xlim(0, max_it*dt)
    ax1.grid()
    ax2.set_ylim(-1, max_power+1)
    ax2.set_xlim(-0.5, 5)
    ax2.grid()

    for ax in [ax1, ax2]:
        ax.figure.canvas.draw()

    line1, = ax1.plot([],[])
    line2, = ax2.plot([],[])
    line3, = ax1.plot([],[], color='red', linewidth=3)
    line4, = ax2.plot([],[], color='red', linewidth=3)
    lines = [line1, line2, line3, line4]

    ax1.set_xlabel('Time [days]')
    ax1.set_ylabel('Average Energy per Node')
    ax2.set_xlabel('P/C')
    ax2.set_ylabel('Average Energy per Node')

    plt.subplots_adjust(wspace=0.5)

    def animate(i):
        if i > 1:
            lines[0].set_data(np.linspace(0, (i-2)*dt, i-2), status[:(i-2),0])
            lines[1].set_data(status[:(i-2),1], status[:(i-2),0])
        if i > 5:
            lines[2].set_data(np.linspace((i-3)*dt, i*dt, 3), status[(i-3):i,0])
            lines[3].set_data(status[(i-3):i, 1], status[(i-3):i, 0])

        return lines

    anim = animation.FuncAnimation(fig, animate, frames=max_it, interval=20, blit=True)

    # seconds = 30
    # fps = max_it / seconds
    # anim.save("mean_field_down.mp4", fps=fps)

    if jupyter:
        return anim
    else:
        plt.show()


if __name__ == "__main__":
    # set independent variables for the system
    N = 50                  # Number of nodes
    max_it = 500            # Number of iterations
    a = 2                   # Amplitude sine function
    dt = 0.01               # Integration step
    max_power = 12          # Battery Capacity

    # set dependent variables
    status = np.zeros((max_it, 2))

    # for t in range(max_it):
    #     G, C = use_power(G, a, dt*t)
    #     G, P = generate_power(G, a, dt*t, max_power)
    #     status[t, 0] = get_global_status(G)
    #     status[t, 1] = P / C

    animate_meanfield(status, max_power, max_it, dt, jupyter=True)
