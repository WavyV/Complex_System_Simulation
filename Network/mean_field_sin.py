import networkx as nx
from matplotlib import pyplot as plt
import random
import numpy as np


def initialize(N):
    G = nx.Graph()
    for i in range(N):
        G.add_node(i)
    for i in range(N):
        for j in range(N):
            if i != j:
                G.add_edge(i, j)

    for node in G.nodes():
        G.node[node]['power'] = 5
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


def use_power(G, a, t):
    C = a / np.pi  # Stable situation, overall production = consumption. If < then shortage, if > then buildup of energy stored
    t = t % 1
    #C = a * np.sin(np.pi * t)  # Oscillating consumption
    for node in G.nodes():
        G.node[node]['power'] -= C
    return G, C


def get_global_status(G):
    total_power = 0
    for node in G.nodes():
        total_power += G.node[node]['power']
    return total_power / len(G.nodes())



N = 50
max_it = 500
a = 1
G = initialize(N)
dt = 0.01
max_power = 10

status = np.zeros((max_it, 2))

for t in range(max_it):
    G, C = use_power(G, a, dt*t)
    G, P = generate_power(G, a, dt*t, max_power)
    status[t, 0] = get_global_status(G)
    status[t, 1] = P / C


plt.plot(range(1, max_it+1), status[:,0])
plt.ylabel('Average Energy per Node')
plt.xlabel('Iteration')
plt.show()

plt.plot(status[:,1], status[:,0])
plt.ylabel('Average Energy per Node')
plt.xlabel('P/C')
plt.show()
