import networkx as nx
from matplotlib import pyplot as plt
import random
import numpy as np
import scipy.stats
import datetime
from matplotlib import animation
from copy import deepcopy
from matplotlib.patches import Patch

def initialize(N, cls, min_power, alphas, p=0, k=0):
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
        G.node[node]['alpha'] = alphas[alpha]*0.01
        G.node[node]['surplus'] = 0
        G.node[node]['alloc'] = 0
    return G

def generate_power(G, P, max_power):
    for i, node in enumerate(G.nodes()):
        if G.node[node]['power'] == 0:
            continue
        G.node[node]['power'] += G.node[node]['alpha'] * P
    return G

def send_power(G, min_power):
    for node in G.nodes():
        if G.node[node]['power'] > min_power:
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

def use_power(G, exp_alpha):
    for node in G.nodes():
        if G.node[node]['power'] == 0:
            continue
        G.node[node]['power'] -= exp_alpha/np.pi

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


    #

    #
    # # Number of saved cells due to altruism
    # ax4 = plt.subplot(3,3,7)
    # ax4.set_xlim([0, c.step_num_max])
    # ax4.set_ylim([0,(c.n-1)**2+1])
    # ax_saved, = ax4.plot(data_figure)
    # ax4.set_title("Saved cells by energy distribution")
    # ax4.set_xlabel("Days")
    # ax4.set_ylabel("Number of cells")
    # ax4.set_xticks(xtic)
    # ax4.set_xticklabels(xlab)
    #

    #
    # # Average energy per node as a function of the ratio P/C
    # ax6 = plt.subplot(3,3,6)
    # ax6.set_xlim([-0.1, numpy.amax(ratioPC)*1.1])
    # ax6.set_ylim([0, numpy.amax(average_energy)*1.1])
    # ax_ratio, = ax6.plot(data_figure)
    # ax_ratio_red, = ax6.plot(data_figure, data_figure, color='red', linewidth=3)
    # ax6.set_title("Ratio")
    # ax6.set_xlabel('P/C')
    # ax6.set_ylabel('Average Energy per Node')
    #
    # # Cells that died
    # ax7 = plt.subplot(3,3,2)
    # im_died = ax7.imshow(data_imshow, vmin=0, vmax=1, cmap="prism")
    # ax7.set_title("Status cells")
    # ax7.set_xticks([])
    # ax7.set_yticks([])
    # legend_elements = [Patch(facecolor='green', label='Active'), \
    #                     Patch(facecolor='red', label='Inactive')]
    # ax7.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    #
    # # Distributed energy
    # ax8 = plt.subplot(3,3,8)
    # ax8.set_xlim([0, c.step_num_max])
    # ax8.set_ylim([0, numpy.amax(c.STAT_alloc_energy) + 0.1])
    # ax_distributed, = ax8.plot(data_figure)
    # ax8.set_title("Energy distribution")
    # ax8.set_xlabel("Days")
    # ax8.set_ylabel("Energy")
    # ax8.set_xticks(xtic)
    # ax8.set_xticklabels(xlab)
    #
    # # Total Energy level
    # ax9 = plt.subplot(3,3,9)
    # ax9.set_xlim([0, c.step_num_max])
    # ax9.set_ylim([0, numpy.amax(c.STAT_total_energy*1.1)])
    # ax_total_energy, = ax9.plot(data_figure)
    # ax9.set_title("Aggregate energy")
    # ax9.set_xlabel("Days")
    # ax9.set_ylabel("Energy")
    # ax9.set_xticks(xtic)
    # ax9.set_xticklabels(xlab)

    # def init():
    #     ---
    #
    #     return im_energy #, ax_active, im_alpha, ax_saved, ax_sun, ax_ratio, im_died, ax_distributed, ax_total_energy, ax_ratio_red

def init():
    pass

def animate(i):
    # run a step of the simulation
    global G
    global N
    global max_power
    global production
    global active
    G = generate_power(G, production[i], max_power)
    G = send_power(G, min_power)
    G = update_power(G, max_power)
    G = use_power(G, exp_alpha * dt)

    # calculate values
    energy = [G.node[node]['power'] for node in G.nodes()]
    status = [1 if G.node[node]['power'] > 0 else 0 for node in G.nodes()]
    prod = [G.node[node]['alpha'] * production[i] for node in G.nodes()]
    if i < max_it
        active.append(np.sum(status)/N)

    # animate the energy level of the network
    axes[0,0].clear()
    nx.draw(G, nx.spring_layout(G, random_state=1), node_color=energy, ax=axes[0,0], vmin=0, vmax=max_power)
    axes[0,0].set_title("Energy levels")

    # animate status of cells
    axes[0,1].clear()
    nx.draw(G, nx.spring_layout(G, random_state=1), node_color=status, ax=axes[0,1], vmin=0, vmax=1, cmap="prism")
    axes[0,1].set_title("Status cells")

    # animate solar production
    axes[0,2].clear()
    nx.draw(G, nx.spring_layout(G, random_state=1), node_color=prod, ax=axes[0,2], vmin=0, vmax=a_max*0.31831)
    axes[0,2].set_title("Status cells")

    # animate the sun
    ax_sun.set_data(np.arange(i), production[:i])

    # animate
    print("i = " + str(i))
    print(len(np.arange(i+1)), len(active))
    ax_active.set_data(np.arange(i+1), active)

    fig.suptitle(i)

    return ax_sun, ax_active

if __name__ == "__main__":

    # set parameters of the system
    N = 50
    days = 2
    max_it = 30
    init_power = 1
    min_power = 1
    a_max = 10 * 0.31831
    a_min = 0
    exp_alpha = (a_max+a_min)/2 * 0.31831
    max_power = 2
    p = 0.5
    k = 4

    dt = days / max_it

    alphas = np.random.uniform(a_min, a_max, N)

    G = initialize(N,'random', init_power, alphas, p=p)

    steps = np.linspace(0, max_it*dt, num=max_it)
    production = np.clip(np.sin(2*np.pi*steps), a_min=0, a_max=None)

    # ANIMATION
    save = False
    # initialize figure
    fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(13,8))
    # fig.suptitle(f"Parameters:  N= {c.n**2},  Alpha ~ U[{c.alpha_min_per_day},{c.alpha_max_per_day}],  Beta = {round(c.beta_per_day,2)},  Max energy = {c.energy_max},\n  Min energy = {c.energy_min},  Max transfer = {c.max_transfer},  Cells can die = {c.cells_can_die},  Take panels if died = {c.take_panels_if_died}")

    # Set days label for animation
    xtic = [x for x in range(max_it) if x % int(max_it / days) == 0]
    xlab = [d for d in range(days+1)]

    fig.suptitle(0)

    # Energy levels on network
    nx.draw(G, nx.spring_layout(G, random_state=1), ax=axes[0,0], vmin=0, vmax=max_power)
    axes[0,0].set_title("Energy levels")

    # Status of nodes
    nx.draw(G, nx.spring_layout(G, random_state=1), ax=axes[0,1], vmin=0, vmax=1, cmap="prism")
    axes[0,1].set_title("Status cells")

    # Value of alpha on the grid as a function of the sun
    nx.draw(G, nx.spring_layout(G, random_state=1), ax=axes[0,2], vmin=0, vmax=a_max)
    axes[0,2].set_title("Energy production")

    # Total active cells
    axes[1,0].set_xlim([0, max_it])
    axes[1,0].set_ylim([0,1.05])
    axes[1,0].set_title("Number of active nodes")
    ax_active, = axes[1,0].plot([],[])
    axes[1,0].set_xlabel("Time")
    axes[1,0].set_ylabel("Active (%)")

    # Sun
    axes[1,1].set_xlim([0, max_it])
    axes[1,1].set_ylim([0,1.05])
    ax_sun, = axes[1,1].plot([],[])
    axes[1,1].set_title("Sun")
    axes[1,1].set_xlabel("Days")
    axes[1,1].set_ylabel(r"$\max(\sin(2\pi t,0)$")
    axes[1,1].set_xticks(xtic)
    axes[1,1].set_xticklabels(xlab)

    plt.tight_layout(pad=1.0, w_pad=3.0, h_pad=1.0, rect=(0,0,1,0.92))

    # variables to record statistics
    active = []

    # run the animation function
    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=range(0, max_it), interval=1, blit=False)
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
