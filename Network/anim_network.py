import networkx as nx
from matplotlib import pyplot as plt
import random
import numpy as np
import scipy.stats
import datetime
from matplotlib import animation
from copy import deepcopy
from matplotlib.patches import Patch

def initialize(N, cls, min_power, alphas, dt, p=0, k=0):
    if cls == 'random':
        G =  nx.erdos_renyi_graph(N, p)
    elif cls == 'watts':
        G = nx.connected_watts_strogatz_graph(N, k=k, p=p)
    elif cls == 'ring':
        G = nx.watts_strogatz_graph(N, k=k, p=0)
    elif cls == 'barabasi':
        G = nx.powerlaw_cluster_graph(N, m=k, p=p)
    else:
        G = nx.Graph()
        for i in range(N):
            G.add_node(i)
        for i in range(N):
            for j in range(N):
                if i != j:
                    G.add_edge(i, j)
    for alpha, node in enumerate(G.nodes()):
        G.node[node]['power'] = min_power
        G.node[node]['alpha'] = alphas[alpha]
        G.node[node]['surplus'] = 0
        G.node[node]['alloc'] = 0
    return G

def generate_power(G, P, max_power):
    for i, node in enumerate(G.nodes()):
        if G.node[node]['power'] == 0:
            continue
        G.node[node]['power'] += G.node[node]['alpha'] * P
    return G

def send_power(G, min_power, share_energy):
    for node in G.nodes():
        if G.node[node]['power'] > min_power and share_energy:
            G.node[node]['surplus'] = G.node[node]['power'] - min_power
        else:
            G.node[node]['surplus'] = 0

        neighbors = list(G.neighbors(node))
        for neighbor in neighbors:
            G.node[neighbor]['alloc'] += G.node[node]['surplus']/len(neighbors)
    return G

def update_power(G, max_power):
    for node in G.nodes():
        if G.node[node]['power'] == 0:
            continue

        G.node[node]['power'] = G.node[node]['power'] + G.node[node]['alloc'] - G.node[node]['surplus']
        #Reset it back to 0
        G.node[node]['surplus'] = 0
        G.node[node]['alloc'] = 0
    return G

def use_power(G, beta):
    for node in G.nodes():
        if G.node[node]['power'] == 0:
            continue
        G.node[node]['power'] -= beta

        if G.node[node]['power'] > max_power:
            G.node[node]['power'] = max_power
        if G.node[node]['power'] < 0:
            G.node[node]['power'] = 0
    return G

def get_global_status(G):
    total_power = sum([G.node[node]['power'] for node in G.nodes()])
    return total_power / len(G.nodes())

def get_local_status(G):
    return np.array([G.node[node]['power'] for node in G.nodes()])

def init():
    pass

def animate(i):
    # set global variables
    global G
    global N
    global beta
    global exp_alpha
    global max_power
    global dependent_nodes
    global production
    global active
    global aggregate
    global average_energy
    global ratioPC
    global saved
    global allocated_power
    global share_energy

    # run a step of simulation
    G = generate_power(G, production[i], max_power)
    G = send_power(G, min_power, share_energy)

    # intermediate recording of statistics
    increased_power = [1 if G.node[node]['alloc'] - G.node[node]['surplus'] > 0 else 0 for node in G.nodes()]
    allocated_power.append(np.sum(np.asarray([G.node[node]['alloc'] for node in G.nodes()])))

    # continue step of simulation
    G = update_power(G, max_power)
    G = use_power(G, beta)

    # calculate values for animation
    energy = [G.node[node]['power'] for node in G.nodes()]
    status = [1 if G.node[node]['power'] > 0 else 0 for node in G.nodes()]
    prod = [G.node[node]['alpha'] * production[i] for node in G.nodes()]
    cons = np.sum(np.asarray(status) * (exp_alpha/np.pi))

    if i <= max_it:
        ratioPC.append(np.sum(prod) / cons)
        active.append(np.sum(status)/N)
        aggregate.append(np.sum(energy))
        average_energy.append(aggregate[i]/(active[i]*N))
        saved.append(np.sum(np.asarray(increased_power) * np.asarray(dependent_nodes)))


    # animate the energy level of the network
    axes[0,0].clear()
    nx.draw(G, nx.spring_layout(G, random_state=1), node_color=energy, ax=axes[0,0], vmin=0, vmax=max_power)
    axes[0,0].set_title("Energy levels")

    # animate status of cells
    axes[0,1].clear()
    nx.draw(G, nx.spring_layout(G, random_state=1), node_color=status, ax=axes[0,1], vmin=0, vmax=1, cmap="prism")
    axes[0,1].set_title("Status cells")
    legend_elements = [Patch(facecolor='green', label='Active'), \
                        Patch(facecolor='red', label='Inactive')]
    axes[0,1].legend(handles=legend_elements, loc=0, borderaxespad=0.)

    # animate solar production in network
    axes[0,2].clear()
    nx.draw(G, nx.spring_layout(G, random_state=1), node_color=prod, ax=axes[0,2], vmin=0, vmax=a_max/steps_per_day)
    axes[0,2].set_title("Energy production")

    # animate number of active
    ax_active.set_data(np.arange(i+1), active)

    # animate the sun
    ax_sun.set_data(np.arange(i), production[:i])

    # animate ratio P/C
    ax_ratio.set_data(ratioPC[:i], average_energy[:i])
    if i>3:
        ax_ratio_red.set_data(ratioPC[i-2:i], average_energy[i-2:i])

    # animate saved cells
    ax_saved.set_data(np.arange(i), saved[:i])

    # animate energy distribution
    ax_distributed.set_data(np.arange(i), allocated_power[:i])

    # animate aggregate energy
    ax_total_energy.set_data(np.arange(i), aggregate[:i])

    return ax_sun, ax_active, ax_total_energy, ax_ratio, ax_ratio_red, ax_saved, ax_distributed

if __name__ == "__main__":

    # set independent variables of the system
    N = 20                 # number of nodes in the network
    days = 10               # number of days to simulate
    max_it = 300            # amount of steps
    init_power = 1          # initial energy for each node
    min_power = 1           # minimal energy nodes keep for themselves, the rest is shared with the neighbors
    max_power = 2           # maximum energy nodes can have
    a_max = 10              # maxium alpha
    a_min = 0               # minimum alpha
    p = 0.5                 # probability of edge formation
    k = 4                   #
    share_energy = False    # whether nodes can share energy

    # set dependent variables of the system
    dt = days / max_it
    steps_per_day = max_it / days
    exp_alpha = (a_max+a_min)/2
    beta = exp_alpha / np.pi / steps_per_day
    alphas = np.random.uniform(a_min, a_max, N) / steps_per_day

    # initialize a network
    G = initialize(N,'random', init_power, alphas, dt, p=p)

    # calculate the dependent nodes (alpha is less than beta)
    dependent_nodes = [1 if G.node[node]['alpha'] > beta else 0 for node in G.nodes()]

    # calculate value of sun
    steps = np.linspace(0, max_it*dt, num=max_it)
    production = np.clip(np.sin(2*np.pi*steps), a_min=0, a_max=None)

    #############
    # ANIMATION #
    save = False
    # initialize figure
    fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(13,8))
    fig.suptitle(f"Parameters:  N= {N},  Alpha ~ U[{a_min},{a_max}],  Beta = {round(exp_alpha / np.pi,2)},  Max energy = {max_power},\n  Min energy = {min_power},  Transfer = {share_energy}")

    # Set days label for animation
    xtic = [x for x in range(max_it) if x % int(max_it / days) == 0]
    xlab = [d for d in range(days+1)]

    # Energy levels on network
    nx.draw(G, nx.spring_layout(G, random_state=1), ax=axes[0,0], vmin=0, vmax=max_power)
    axes[0,0].set_title("Energy levels")
    sm = plt.cm.ScalarMappable(norm=plt.Normalize(vmin=0, vmax=max_power))
    sm.set_array([])
    fig.colorbar(sm, ax=axes[0,0])

    # Status of nodes
    nx.draw(G, nx.spring_layout(G, random_state=1), ax=axes[0,1], vmin=0, vmax=1, cmap="prism")
    axes[0,1].set_title("Status nodes")
    legend_elements = [Patch(facecolor='green', label='Active'), \
                        Patch(facecolor='red', label='Inactive')]
    axes[0,1].legend(handles=legend_elements, loc=0, borderaxespad=0.)

    # Value of alpha on the grid as a function of the sun
    nx.draw(G, nx.spring_layout(G, random_state=1), ax=axes[0,2], vmin=0, vmax=a_max/steps_per_day)
    axes[0,2].set_title("Energy production")
    sm = plt.cm.ScalarMappable(norm=plt.Normalize(vmin=0, vmax=a_max/steps_per_day))
    sm.set_array([])
    fig.colorbar(sm, ax=axes[0,2])

    # Total active cells
    axes[1,0].set_xlim([0, max_it])
    axes[1,0].set_ylim([0,1.05])
    axes[1,0].set_title("Active nodes")
    ax_active, = axes[1,0].plot([],[])
    axes[1,0].set_xlabel("Days")
    axes[1,0].set_ylabel("Active (%)")
    axes[1,0].set_xticks(xtic)
    axes[1,0].set_xticklabels(xlab)

    # Sun
    axes[1,1].set_xlim([0, max_it])
    axes[1,1].set_ylim([0,1.05])
    ax_sun, = axes[1,1].plot([],[])
    axes[1,1].set_title("Sun")
    axes[1,1].set_xlabel("Days")
    axes[1,1].set_ylabel("Intensity")
    axes[1,1].set_xticks(xtic)
    axes[1,1].set_xticklabels(xlab)

    # Average energy per node as a function of the ratio P/C
    axes[1,2].set_xlim([-0.1, exp_alpha/(exp_alpha/np.pi)])
    axes[1,2].set_ylim([0, max_power*1.1])
    ax_ratio, = axes[1,2].plot([],[])
    ax_ratio_red, = axes[1,2].plot([],[], color='red', linewidth=3)
    axes[1,2].set_title("Ratio")
    axes[1,2].set_xlabel('P/C')
    axes[1,2].set_ylabel('Average Energy per Node')

    # Number of saved cells due to altruism
    axes[2,0].set_xlim([0, max_it])
    axes[2,0].set_ylim([0,N])
    ax_saved, = axes[2,0].plot([],[])
    axes[2,0].set_title("Saved cells by energy distribution")
    axes[2,0].set_xlabel("Days")
    axes[2,0].set_ylabel("Number of cells")
    axes[2,0].set_xticks(xtic)
    axes[2,0].set_xticklabels(xlab)

    # Distributed energy
    axes[2,1].set_xlim([0, max_it])
    axes[2,1].set_ylim([0, 10])
    ax_distributed, = axes[2,1].plot([],[])
    axes[2,1].set_title("Energy distribution")
    axes[2,1].set_xlabel("Days")
    axes[2,1].set_ylabel("Energy")
    axes[2,1].set_xticks(xtic)
    axes[2,1].set_xticklabels(xlab)

    # Total Energy level
    axes[2,2].set_xlim([0, max_it])
    axes[2,2].set_ylim([0, np.amax(N*max_power*1.1)])
    ax_total_energy, = axes[2,2].plot([],[])
    axes[2,2].set_title("Aggregate energy")
    axes[2,2].set_xlabel("Days")
    axes[2,2].set_ylabel("Energy")
    axes[2,2].set_xticks(xtic)
    axes[2,2].set_xticklabels(xlab)

    plt.tight_layout(pad=1.0, w_pad=3.0, h_pad=2.0, rect=(0,0,1,0.92))

    # variables to record statistics
    active = []
    aggregate = []
    average_energy = []
    ratioPC = []
    saved = []
    allocated_power = []

    # run the animation function
    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=range(0, max_it), interval=1, blit=False, repeat=False)
    plt.show()

    """
    if save:
        # define the number of seconds your video must be
        now = datetime.datetime.now()
        print(f"Save as: network_animation_date:{now.day}_{now.hour}:{now.minute}.mp4")
        seconds = 30
        fps = c.step_num_max / seconds
        anim.save(f"results/CA_animation_date:{now.day}_{now.hour}:{now.minute}.mp4", fps=fps)
    else:
        # if not save, then show the animation

    """