import numpy
import matplotlib.pyplot as plt
from matplotlib import animation
from copy import deepcopy
from matplotlib.patches import Patch
import datetime

# create cellular automata class
class CA(object):
    def __init__(self,
                 n = 100,
                 days = 7,
                 max_step = 1000,
                 energy_start = 100,
                 alpha_min = 0,
                 alpha_max = 1,
                 beta = 1,
                 energy_max = 10,
                 energy_min = 10,
                 max_transfer = 10,
                 cells_can_die = True,
                 take_panels_if_died = False):
        """
        Initializes the cellular automata:
        :param n:                       the grid size is (n x n). Living cells: (n-2) x (n-2).
        :param dt:                      time interval
        :param max_step:                maximum number of steps
        :param energy_start:            initial amount of energy in the batteries
        :param alpha_min:               minimal value alpha (production per day)
        :param alpha_max:               maximal value alpha -> production = uniform(alpha_min, alpha_max)*sin(...)
        :param beta:                    consumption / time step
        :param energy_max:              maximum storage capacity
        :param energy_min:              above this level the energy is reallocated
        :param cells_can_die:           Whether or not cells can die
        :param take_panels_if_died:     Whether you can take your neighbours solar panels if he died:
        """

        # Set variables
        self.n = n
        self.energy_max = energy_max
        self.energy_min = energy_min
        self.max_transfer = max_transfer

        # Time
        self.t = 0
        self.days = days
        self.dt = days / max_step
        self.step_num = 0
        self.step_num_max = max_step
        self.step_per_day = max_step / days

        # Energy
        self.energy = numpy.zeros([n, n], dtype=numpy.float32)
        self.energy[1:n - 1, 1:n - 1] = energy_start
        self.energy_new_alloc = numpy.zeros([n, n])
        self.energy_new_prod = numpy.zeros([n, n])

        # Alpha
        self.alpha = numpy.zeros([n, n])
        self.alpha_initial = numpy.zeros([n, n])
        self.alpha_new_alloc = numpy.zeros([n, n])
        self.alpha_min_per_day = alpha_min
        self.alpha_max_per_day = alpha_max
        self.alpha_min = alpha_min / self.step_per_day
        self.alpha_max = alpha_max / self.step_per_day
        self.alpha[1:n - 1, 1:n - 1] = numpy.random.uniform(self.alpha_min, self.alpha_max, size=[n - 2, n - 2])
        self.alpha_initial[1:n - 1, 1:n - 1] = numpy.random.uniform(self.alpha_min, self.alpha_max, size=[n - 2, n - 2])

        # Beta
        self.beta_per_day = beta
        self.beta = beta / self.step_per_day

        # Neighbours
        self.friend_n = numpy.zeros([n, n])

        # Cells can die and take panels if died
        self.cells_can_die = cells_can_die
        self.take_panels_if_died = take_panels_if_died

        # Saved cells
        self.saved_cells = numpy.zeros([n, n])

        # STATS
        self.STAT_alloc_energy = numpy.zeros(max_step)
        self.STAT_alloc_panels = numpy.zeros(max_step)
        self.STAT_total_active = numpy.zeros(max_step)
        self.STAT_total_active_abs = numpy.zeros(max_step)
        self.STAT_total_energy = numpy.zeros(max_step)
        self.STAT_sun = numpy.zeros(max_step)
        self.STAT_total_production = numpy.zeros(max_step)
        self.STAT_total_consumption = numpy.zeros(max_step)
        self.STAT_total_alpha = numpy.zeros(max_step)
        self.STAT_saved = numpy.zeros(max_step)

        self.grid = numpy.zeros([n, n, max_step])
        self.grid_prod = numpy.zeros([n, n, max_step])

        # Initial stats
        self.STAT_saved[0] = 0
        self.STAT_alloc_energy[0] = 0
        self.STAT_alloc_panels[0] = 0
        self.STAT_total_active[0] = 1.0
        self.STAT_total_active_abs[0] = self.n **2
        self.STAT_total_energy[0] = numpy.sum(self.energy)
        self.STAT_sun[0]  = self.prod_func(1, self.t)
        self.STAT_total_production[0] = 0
        self.STAT_total_consumption[0] = 0
        self.STAT_total_alpha[0] = numpy.sum(self.alpha)

        self.grid[:,:,0] = self.energy
        self.grid_prod[:,:,0] = self.energy_new_prod

    def step(self):
        # Time
        self.step_num = self.step_num + 1
        self.t = self.t + self.dt

        # Count living neighbours
        self.count_neighbours()

        # Produce energy
        self.produce_energy()

        # Allocate energy
        self.get_energy()

        # Consume energy
        self.consume()

        # Get solar panels from neighbours if take_panels_if_died = True
        self.get_panels()

        # Record stats
        self.STAT_alloc_energy[self.step_num] = numpy.sum(self.energy_new_alloc)
        self.STAT_alloc_panels[self.step_num] = numpy.sum(self.alpha_new_alloc)
        self.STAT_total_active[self.step_num] = numpy.sum(1.0*(self.energy>0))/(self.n-2)**2
        self.STAT_total_active_abs[self.step_num] = numpy.sum(1.0*(self.energy>0))
        self.STAT_total_energy[self.step_num] = numpy.sum(self.energy)
        self.STAT_sun[self.step_num] = self.prod_func(1, self.t)
        self.STAT_total_production[self.step_num] = numpy.sum(self.energy_new_prod)
        self.STAT_total_consumption[self.step_num] = self.beta * numpy.sum(1.0*(self.energy>0))
        self.STAT_total_alpha[self.step_num] = numpy.sum(self.alpha)

        self.grid[:,:, self.step_num] = self.energy
        self.grid_prod[:,:, self.step_num] = self.energy_new_prod

        return self.energy

    def count_neighbours(self):
        """
        Fill the self.friend_n matrix with the number of living/active neighbours of all cells.
        :return: nothing.
        """
        for i in numpy.arange(1, self.n - 1):
            for j in numpy.arange(1, self.n - 1):
                self.friend_n[i, j] = 1 * (self.energy[i - 1, j] > 0) + \
                                      1 * (self.energy[i + 1, j] > 0) + \
                                      1 * (self.energy[i, j - 1] > 0) + \
                                      1 * (self.energy[i, j + 1] > 0)

    def prod_func(self, A, x):
        """
        Computes production from the coefficient matrix and time.
        Production = A*sin(2*pi*x_) where x_=x%1 and 0<x<inf.
        :param A: Coefficient matrix
        :param x: Time
        :return: Production in a matrix
        """

        # Cast between 0 and 1:
        x_1 = x % 1
        if x_1 < 0.5:
            return A * numpy.sin(2 * numpy.pi * x_1)
        else:
            return numpy.zeros_like(A)

    def produce_energy(self):
        """
        Adds energy to the storage
        :return: nothing.
        """
        # Calculate production for each cells
        self.energy_new_prod = self.prod_func(self.alpha, self.t)

        # Increase energy levels
        self.energy = self.energy + self.energy_new_prod

    def get_energy(self):
        """
        If someone is altruistic, gives energy to its neighbours.
        If alpha_min equals alpha_min, cells keep energy for themselves.
        :return: nothing.
        """
        # Allocation is uniform among the neighbours
        self.energy_new_alloc = numpy.zeros([self.n, self.n])
        self.saved_cells = numpy.zeros([self.n, self.n])

        energy_plus = numpy.maximum(0, self.energy - self.energy_min)
        self.STAT_alloc_energy[self.step_num] = numpy.sum(energy_plus)
        energy_per_neighbour = numpy.zeros_like(energy_plus)
        energy_per_neighbour[self.friend_n > 0] = energy_plus[self.friend_n > 0] / self.friend_n[
            self.friend_n > 0]

        for i in numpy.arange(1, self.n - 1):
            for j in numpy.arange(1, self.n - 1):
                if self.energy[i, j] > 0:
                    self.energy_new_alloc[i, j] = min(energy_per_neighbour[i - 1, j], self.max_transfer) + min(energy_per_neighbour[i + 1, j], self.max_transfer) + \
                                                  min(energy_per_neighbour[i, j - 1], self.max_transfer) + min(energy_per_neighbour[i, j + 1], self.max_transfer)

                    # Check if without this amount, it would stop working
                    self.saved_cells[i, j] = 1.0*((self.alpha[i, j] < self.beta / 0.31831) and (self.energy_new_alloc[i, j] - energy_plus[i, j] + max(energy_plus[i,j] - self.friend_n[i,j] * self.max_transfer, 0) > 0))

                    self.STAT_saved[self.step_num] += self.saved_cells[i, j]

                    # The new amount of energy = old energy - the energy you potentially distrubute + the energy you receive + the energy you could not distribute (max_transfer)
                    self.energy[i, j] = self.energy[i, j] - energy_plus[i, j] + self.energy_new_alloc[i, j] + max(energy_plus[i,j] - self.friend_n[i,j] * self.max_transfer, 0)

    def consume(self):
        # Each node consumes energy
        self.energy = self.energy - self.beta
        self.energy[self.energy < 0] = 0

        # Now the maximum can be set
        self.energy[self.energy > self.energy_max] = self.energy_max

    def get_panels(self):
        # Distrubte solar panels if cell died
        if self.take_panels_if_died and self.cells_can_die:
            self.alpha_new_alloc = numpy.zeros([self.n, self.n])
            alpha_per_neighbour = numpy.zeros_like(self.alpha_new_alloc)
            alpha_per_neighbour[self.friend_n > 0] = self.alpha[self.friend_n > 0] / self.friend_n[
                self.friend_n > 0]
            # Only if there is no energy
            alpha_per_neighbour[self.energy > 0] = 0

            # If it has only one neighbour, it takes all panels
            for i in numpy.arange(1, self.n - 1):
                for j in numpy.arange(1, self.n - 1):
                    self.alpha_new_alloc[i, j] = alpha_per_neighbour[i - 1, j] + alpha_per_neighbour[i + 1, j] + \
                                                 alpha_per_neighbour[i, j - 1] + alpha_per_neighbour[i, j + 1]

            self.alpha += self.alpha_new_alloc

        # set alpha to zero if cell has no energy left
        if self.cells_can_die:
            self.alpha[self.energy == 0] = 0

def animate_CA():
    # run CA for ma
    for i in range(c.step_num_max-1):
        c.step()

    # Print potential production and consumption
    potential_prod = numpy.sum(c.STAT_sun * numpy.sum(c.alpha_initial[1:c.n - 1, 1:c.n - 1]))
    potential_cons = c.beta * c.step_num_max * ((c.n-2) ** 2)
    ratio_prod_cons = potential_prod / potential_cons
    print("Potential production: " + str(potential_prod))
    print("Potential consumption: " + str(potential_cons))
    print("Ratio production / consumption: " + str(ratio_prod_cons))

    # Run some calculations for visualisation and animation
    # Calculate ratio production over consumption and average energy per node
    ratioPC = numpy.nan_to_num(c.STAT_total_production / c.STAT_total_consumption)
    average_energy = numpy.nan_to_num(c.STAT_total_energy / c.STAT_total_active_abs)

    # Set dead_cell to zero
    dead_cells = deepcopy(c.grid)
    dead_cells[dead_cells > 0] = 1

    # animate the results
    # initialize figure
    fig = plt.figure(figsize=(13,8))
    fig.suptitle(f"Parameters:  N= {c.n**2},  Alpha ~ U[{c.alpha_min_per_day},{c.alpha_max_per_day}],  Beta = {round(c.beta_per_day,2)},  Max energy = {c.energy_max},\n  Min energy = {c.energy_min},  Max transfer = {c.max_transfer},  Cells can die = {c.cells_can_die},  Take panels if died = {c.take_panels_if_died}")

    data_figure = numpy.zeros(c.step_num_max)
    data_imshow = numpy.zeros((c.n-2, c.n-2))

    # Set days label for animation
    xtic = [x for x in range(c.step_num_max) if x % int(c.step_per_day) == 0]
    xlab = [d for d in range(c.days+1)]

    # Energy levels on grid
    ax1 = plt.subplot(3,3,1)
    im_energy = ax1.imshow(data_imshow, vmin=0, vmax=c.energy_max)
    ax1.set_title("Energy levels")
    fig.colorbar(im_energy, ax=ax1)
    ax1.set_xticks([])
    ax1.set_yticks([])

    # Total active cells
    ax2 = plt.subplot(3,3,4)
    ax2.set_xlim([0, c.step_num_max])
    ax2.set_ylim([0,1.05])
    ax2.set_title("Number of active nodes")
    ax_active, = ax2.plot(data_figure)
    ax2.set_xlabel("Days")
    ax2.set_ylabel("Active (%)")
    ax2.set_xticks(xtic)
    ax2.set_xticklabels(xlab)

    # Value of alpha on the grid as a function of the sun
    ax3 = plt.subplot(3,3,3)
    ax3.set_title("Energy production")
    im_alpha = ax3.imshow(data_imshow, vmin=0, vmax=c.alpha_max)
    fig.colorbar(im_alpha, ax=ax3)
    ax3.set_xticks([])
    ax3.set_yticks([])

    # Number of saved cells due to altruism
    ax4 = plt.subplot(3,3,7)
    ax4.set_xlim([0, c.step_num_max])
    ax4.set_ylim([0,(c.n-1)**2+1])
    ax_saved, = ax4.plot(data_figure)
    ax4.set_title("Saved cells by energy distribution")
    ax4.set_xlabel("Days")
    ax4.set_ylabel("Number of cells")
    ax4.set_xticks(xtic)
    ax4.set_xticklabels(xlab)

    # Value of the sun
    ax5 = plt.subplot(3,3,5)
    ax5.set_xlim([0, c.step_num_max])
    ax5.set_ylim([0,1.05])
    ax_sun, = ax5.plot(data_figure)
    ax5.set_title("Sun")
    ax5.set_xlabel("Days")
    ax5.set_ylabel(r"$\max(\sin(2\pi t,0)$")
    ax5.set_xticks(xtic)
    ax5.set_xticklabels(xlab)

    # Average energy per node as a function of the ratio P/C
    ax6 = plt.subplot(3,3,6)
    ax6.set_xlim([-0.1, numpy.amax(ratioPC)*1.1])
    ax6.set_ylim([0, numpy.amax(average_energy)*1.1])
    ax_ratio, = ax6.plot(data_figure)
    ax_ratio_red, = ax6.plot(data_figure, data_figure, color='red', linewidth=3)
    ax6.set_title("Ratio")
    ax6.set_xlabel('P/C')
    ax6.set_ylabel('Average Energy per Node')

    # Cells that died
    ax7 = plt.subplot(3,3,2)
    im_died = ax7.imshow(data_imshow, vmin=0, vmax=1, cmap="prism")
    ax7.set_title("Status cells")
    ax7.set_xticks([])
    ax7.set_yticks([])
    legend_elements = [Patch(facecolor='green', label='Active'), \
                        Patch(facecolor='red', label='Inactive')]
    ax7.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

    # Distributed energy
    ax8 = plt.subplot(3,3,8)
    ax8.set_xlim([0, c.step_num_max])
    ax8.set_ylim([0, numpy.amax(c.STAT_alloc_energy) + 0.1])
    ax_distributed, = ax8.plot(data_figure)
    ax8.set_title("Energy distribution")
    ax8.set_xlabel("Days")
    ax8.set_ylabel("Energy")
    ax8.set_xticks(xtic)
    ax8.set_xticklabels(xlab)

    # Total Energy level
    ax9 = plt.subplot(3,3,9)
    ax9.set_xlim([0, c.step_num_max])
    ax9.set_ylim([0, numpy.amax(c.STAT_total_energy*1.1)])
    ax_total_energy, = ax9.plot(data_figure)
    ax9.set_title("Aggregate energy")
    ax9.set_xlabel("Days")
    ax9.set_ylabel("Energy")
    ax9.set_xticks(xtic)
    ax9.set_xticklabels(xlab)

    plt.tight_layout(pad=1.0, w_pad=3.0, h_pad=1.0, rect=(0,0,1,0.92))

    def init():
        im_energy.set_data(data_imshow)
        ax_active.set_data(data_figure, data_figure)
        im_alpha.set_data(data_imshow)
        ax_saved.set_data(data_figure, data_figure)
        ax_sun.set_data(data_figure, data_figure)
        ax_ratio.set_data(data_figure, data_figure)
        ax_ratio_red.set_data(data_figure, data_figure)
        im_died.set_data(data_imshow)
        ax_distributed.set_data(data_figure, data_figure)
        ax_total_energy.set_data(data_figure, data_figure)

        return im_energy, ax_active, im_alpha, ax_saved, ax_sun, ax_ratio, im_died, ax_distributed, ax_total_energy, ax_ratio_red

    def animate(i):
        im_energy.set_data(c.grid[1:c.n-1,1:c.n-1,i])
        ax_active.set_data(numpy.arange(i), c.STAT_total_active[:i])
        im_alpha.set_data(c.grid_prod[1:c.n-1,1:c.n-1,i])
        ax_saved.set_data(numpy.arange(i), c.STAT_saved[:i])
        ax_sun.set_data(numpy.arange(i), c.STAT_sun[:i])
        ax_ratio.set_data(ratioPC[:i], average_energy[:i])
        im_died.set_data(dead_cells[1:c.n-1,1:c.n-1,i])
        ax_distributed.set_data(numpy.arange(i), c.STAT_alloc_energy[:i])
        ax_total_energy.set_data(numpy.arange(i), c.STAT_total_energy[:i])

        if i>1:
            ax_ratio_red.set_data(ratioPC[i-2:i], average_energy[i-2:i])

        return im_energy, ax_active, im_alpha, ax_saved, ax_sun, ax_ratio, im_died, ax_distributed, ax_total_energy, ax_ratio_red

    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=range(0, c.step_num_max), interval=1, blit=False)

    if save:
        # define the number of seconds your video must be
        now = datetime.datetime.now()
        print(f"Save as: CA_animation_date:{now.day}_{now.hour}:{now.minute}.mp4")
        seconds = 30
        fps = c.step_num_max / seconds
        anim.save(f"results/CA_animation_date:{now.day}_{now.hour}:{now.minute}.mp4", fps=fps)
    else:
        # if not save, then show the animation
        plt.show()


if __name__ == "__main__":

    # set potential production = potential consumption
    alpha_min = 0
    alpha_max = 10
    beta = ((alpha_min + alpha_max) / 2) * 0.31831
    # set number of steps
    max_step = 500

    # initialize CA
    c = CA(n = 50,
           days = 10,
           max_step = 400,
           energy_start = 1.59 / 2,
           alpha_min = alpha_min,
           alpha_max = alpha_max,
           beta = beta,
           energy_max = 1.59,
           energy_min = 1.59,
           max_transfer = 0,
           cells_can_die = True,
           take_panels_if_died = False)

    # save animation if True
    save = False

    # runs and animates the cellular automata
    animate_CA()
