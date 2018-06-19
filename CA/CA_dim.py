# Mask to select neighbours
import numpy
import matplotlib.pyplot as plt
from matplotlib import animation

class CA(object):
    def __init__(self,
                 n=100,
                 dt=0.1,
                 max_step=1000,
                 energy_start=100,
                 alpha_min=0,
                 alpha_max=1,
                 beta=1,
                 energy_max=10,
                 energy_min=10,
                 verbose=True,
                 take_panels_if_died = False):
        """
        Initializes the cellular automata
        :param n: the grid size is (n x n). Living cells: (n-2) x (n-2).
        :param dt: time interval
        :param max_step: maximum number of steps
        :param energy_start: initial amount of energy in the batteries
        :param alpha_min:
        :param alpha_max: production = uniform(alpha_min, alpha_max)*sin(...)
        :param beta: consumption / time step
        :param energy_max: maximum storage capacity
        :param energy_min: above this level the energy is reallocated
        :param verbose: print output
        """

        # Set variables
        self.n = n
        self.energy_max = energy_max
        self.energy_min = energy_min
        self.verbose = verbose

        # Energy
        self.energy = numpy.zeros([n, n], dtype=numpy.float32)
        self.energy[1:n - 1, 1:n - 1] = energy_start
        self.energy_new_alloc = numpy.zeros([n, n])
        self.energy_new_prod = numpy.zeros([n, n])

        # Alpha
        self.alpha = numpy.zeros([n, n])
        self.alpha[1:n - 1, 1:n - 1] = numpy.random.uniform(alpha_min, alpha_max, size=[n - 2, n - 2])
        self.alpha_new_alloc = numpy.zeros([n, n])

        # Beta
        self.beta = beta

        # Time
        self.t = 0
        self.dt = dt
        self.step_num = 0
        self.step_num_max = max_step

        # Neighbours
        self.friend_n = numpy.zeros([n, n])

        self.take_panels_if_died = take_panels_if_died

        # Saved cells
        self.saved_cells = numpy.zeros([n, n])

        # STATS
        self.STAT_alloc_energy = numpy.zeros(max_step)
        self.STAT_alloc_panels = numpy.zeros(max_step)
        self.STAT_total_active = numpy.zeros(max_step)
        self.STAT_total_energy = numpy.zeros(max_step)
        self.STAT_total_production = numpy.zeros(max_step)
        self.STAT_total_alpha = numpy.zeros(max_step)
        self.STAT_saved = numpy.zeros(max_step)

        self.grid = numpy.zeros([n, n, max_step])

        # Initial stats
        self.STAT_saved[0] = 0
        self.STAT_alloc_energy[0] = 0
        self.STAT_alloc_panels[0] = 0
        self.STAT_total_active[0] = 1.0
        self.STAT_total_energy[0] = numpy.sum(self.energy)
        self.STAT_total_production[0] = 0
        self.STAT_total_alpha[0] = numpy.sum(self.alpha)

        self.grid[:,:,0] = self.energy

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

        # Get solar panels from neighbours if steal = True
        if self.take_panels_if_died:
            self.get_panels()

        # Record stats
        self.STAT_alloc_energy[self.step_num] = numpy.sum(self.energy_new_alloc)
        self.STAT_alloc_panels[self.step_num] = numpy.sum(self.alpha_new_alloc)
        self.STAT_total_active[self.step_num] = numpy.sum(1.0*(self.energy>0))/(self.n-2)**2
        self.STAT_total_energy[self.step_num] = numpy.sum(self.energy)
        self.STAT_total_production[self.step_num] = numpy.sum(self.energy_new_prod)
        self.STAT_total_alpha[self.step_num] = numpy.sum(self.alpha)

        self.grid[:,:, self.step_num] = self.energy

        return self.energy

    def count_neighbours(self):
        """
        Fill the self.friend_n matrix with the number of living neighbours of all cells.
        :return: nothing.
        """
        for i in numpy.arange(1, self.n - 1):
            for j in numpy.arange(1, self.n - 1):
                self.friend_n[i, j] = 1 * (self.energy[i - 1, i] > 0) + \
                                      1 * (self.energy[i + 1, i] > 0) + \
                                      1 * (self.energy[i, i - 1] > 0) + \
                                      1 * (self.energy[i, i + 1] > 0)

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
        :return: nothing.
        """
        # Allocation is uniform among the neighbours
        self.energy_new_alloc = numpy.zeros([self.n, self.n])
        self.saved_cells = numpy.zeros([self.n, self.n])

        energy_plus = numpy.maximum(0, self.energy - self.energy_min)
        energy_per_neighbour = numpy.zeros_like(energy_plus)
        energy_per_neighbour[self.friend_n > 0] = energy_plus[self.friend_n > 0] / self.friend_n[
            self.friend_n > 0]

        for i in numpy.arange(1, self.n - 1):
            for j in numpy.arange(1, self.n - 1):
                if self.energy[i, j] > 0:
                    self.energy_new_alloc[i, j] = energy_per_neighbour[i - 1, j] + energy_per_neighbour[i + 1, j] + \
                                                  energy_per_neighbour[i, j - 1] + energy_per_neighbour[i, j + 1]

                    # Check if without this amount, it would stop working
                    self.saved_cells[i, j] = 1.0*((self.energy[i, j]<=self.beta) and
                                                           (self.energy[i, j] - energy_plus[i, j] +
                                                            self.energy_new_alloc[i, j]) > self.beta)

                    self.STAT_saved[self.step_num] += self.saved_cells[i, j]
                    # Get energy
                    self.energy[i, j] = self.energy[i, j] - energy_plus[i, j] + self.energy_new_alloc[i, j]

    def consume(self):
        # Each node consumes energy
        self.energy = self.energy - self.beta
        self.energy[self.energy < 0] = 0

        # Now the maximum can be set
        self.energy[self.energy > self.energy_max] = self.energy_max

    def get_panels(self):

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
        self.alpha[self.energy == 0] = 0

if __name__ == "__main__":

    # Run CA
    c = CA(n = 10,
           dt = 0.1,
           max_step = 100,
           energy_start = 3,
           alpha_min = 0,
           alpha_max = 2,
           beta = 1,
           energy_max = 10,
           energy_min = 0,
           verbose = True,
           take_panels_if_died = False)

           #

    # Draw figures
    for i in range(c.max):
        c.step()

    # print initial grid
    plt.imshow(c.grid[:,:,0], vmin=0, vmax=10)
    plt.show()

    # animate the results
    fig = plt.figure()
    data = numpy.zeros((c.n, c.n))
    im = plt.imshow(data, vmin=0, vmax=10)
    plt.title(0)

    def init():
        im.set_data(data)
        return im,

    def animate(i):
        im.set_data(c.grid[:,:,i])
        plt.title('t = %.3f' % float(i))
        return im,

    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=range(0, 100), interval=1, blit=False)

    # anim.save(f'results/animation_random30_f_{f}__k_{k}.mp4', fps=200)

    plt.show()
