import networkx as nx
from matplotlib import pyplot as plt
import random
import numpy as np


def initialize(N):
    G = nx.barabasi_albert_graph(N, 2)
    color_map = [0] * N
    for node in G.nodes():
        #G.node[node]['power'] = random.randint(-1, 1)
        G.node[node]['power'] = 0
        G.node[node]['status'] = 'alive'
    return G, color_map


def set_color(G):
    for node in G.nodes():
        if G.node[node]['power'] > 0:
            G.node[node]['status'] = 'dead'
            color_map[node] = 'black'
        elif G.node[node]['power'] < 0:
            color_map[node] = 'red'
        else:
            color_map[node] = 'green'
    return color_map


def generate_power(G):
    for node in G.nodes():
        if G.node[node]['status'] == 'alive':
            G.node[node]['power'] += random.randint(0, 2)
    return G


def use_power(G):
    for node in G.nodes():
        if G.node[node]['status'] == 'alive':
            G.node[node]['power'] -= 1
    return G


def send_power(G):
    for node in G.nodes():
        if G.node[node]['status'] == 'alive':
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
    dead = 0
    good = 0
    short = 0
    for node in G.nodes():
        if G.node[node]['status'] == 'dead':
            dead += 1
        elif G.node[node]['power'] == 0:
            good += 1
        elif G.node[node]['power'] < 0:
            short += 1
    return dead, good, short



N = 50
max_it = 100
G, color_map = initialize(N)
color_map = set_color(G)
nx.draw(G, nx.spring_layout(G, random_state=1), node_color=color_map)
plt.show()

status = np.zeros((max_it, 3))

for t in range(max_it):
    G = use_power(G)
    G = generate_power(G)
    G = send_power(G)
    color_map = set_color(G)
    status[t, :] = get_global_status(G)

    # nx.draw(G, nx.spring_layout(G, random_state=1), node_color=color_map)
    # plt.show()

plt.plot(range(1, max_it+1), status[:,0], label='dead', color='black')
plt.plot(range(1, max_it+1), status[:,1], label='good', color='green')
plt.plot(range(1, max_it+1), status[:,2], label='short', color='red')
plt.legend()
plt.ylim(0,N)
plt.ylabel('Number of Nodes')
plt.xlabel('Iteration')
plt.show()
