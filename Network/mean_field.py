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
        G.node[node]['power'] = 0
    return G


def generate_power(G, a):
    for node in G.nodes():
        G.node[node]['power'] += random.randint(0, a)
        #G.node[node]['power'] += random.uniform(0, a)
    return G


def use_power(G):
    for node in G.nodes():
        G.node[node]['power'] -= 1
    return G


def send_power(G):
    for node in G.nodes():
        neighbors = list(G.neighbors(node))
        for neighbor in neighbors:
            if G.node[neighbor]['power'] >= 0:
                neighbors.remove(neighbor)
        for neighbor in neighbors:
            while G.node[neighbor]['power'] < 0 and G.node[node]['power'] > 0:
                G.node[neighbor]['power'] += 1
                G.node[node]['power'] -= 1
    return G


def get_global_status(G):
    total_power = 0
    for node in G.nodes():
        total_power += G.node[node]['power']

    return total_power / len(G.nodes())



N = 50
max_it = 1000
a = 3
G = initialize(N)

status = np.zeros((max_it, 3))

for t in range(max_it):
    G = use_power(G)
    G = generate_power(G, a)
    G = send_power(G)
    status[t, :] = get_global_status(G)


plt.plot(range(1, max_it+1), status[:,0])
plt.ylabel('Average Energy per Node')
plt.xlabel('Iteration')
plt.show()
