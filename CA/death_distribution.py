import numpy
import matplotlib.pyplot as plt
from matplotlib import animation
from copy import deepcopy
from matplotlib.patches import Patch
import datetime
from scipy.ndimage import measurements

# import CA class
from cellular_automata import CA




if __name__ == "__main__":

    # set potential production = potential consumption
    alpha_min = 0
    alpha_max = 10
    beta = 1.5*((alpha_min + alpha_max) / 2) / numpy.pi
    # set number of steps
    max_step = 500

    # initialize CA
    c = CA(n = 150,
           days = 10,
           max_step = 400,
           energy_start = 1.59 / 2,
           alpha_min = alpha_min,
           alpha_max = alpha_max,
           beta = beta,
           energy_max = 1.59,
           energy_min = 1.30,
           max_transfer = 10,
           cells_can_die = True,
           take_panels_if_died = False)

    # run CA for ma
    for i in range(c.step_num_max-1):
        c.step()

    # Set dead_cell to zero
    temp = deepcopy(c.grid)
    dead_cells = deepcopy(c.grid)
    dead_cells[temp == 0] = 1
    dead_cells[temp > 0] = 0

    alive_cells = deepcopy(c.grid)
    alive_cells[temp > 0] = 1

    # calculate areas
    z2 = alive_cells[:,:,399]
    lw, num = measurements.label(z2)
    area = measurements.sum(z2, lw, index=numpy.arange(lw.max() + 1))

    bins = range(0, 50)
    plt.xticks(bins, ["2^%s" % i for i in bins])
    plt.hist(area, log=True, bins=bins)
    plt.show()
