# Complex_System_Simulation
Complex System Simulation - Solar-powered Electrical Grid

Overleaf: https://www.overleaf.com/17205912wqgjtnkbpyvg#/65631220/

Website: https://wavyv.github.io/Complex_System_Simulation/

Youtube (Dimitri): https://www.youtube.com/playlist?list=PLq5YLqLQqDGN9smI9m2DzaxOU3DyvS7Qn

Youtube (Walter): https://www.youtube.com/playlist?list=PLYGKT8n_T51NHXMde8I59YwIajTn1Xf66

# How to run the code

In each directory, you will find the necessary files to execute your own simulation of the electrical grid. If you would like to keep things simple, then open up the Jupyter notebook, set the parameters and execute the code. The animations will pop-up in a few minutes (depending on parameter settings)

## Mean-field

Python:

## Network

Python:




## Cellular Automata

### Python:

After setting the input parameters, the cellular_automata.py file can be run executed to visualize some attributes of the system. We used a class for the CA:

```python
c = CA( n = 100,
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
```
where
- **n** is the size of the grid (n-by-n),
- **days** indicate the length of the time interval,
- **max_step** is the maximum number of steps, energy_start is the initial energy level,
- **alpha_min** and alpha_max denote the minimum and maximum level of production,
- **beta** is the consumption,
- **energy_min** inidicates the level above which the surplus is shared,
- **energy_max** is the maximum capacity of the batteries,
- **max_transfer** is the maximum energy transfer,
- **cells_can_die** let the nodes die and
- **take_panels_if_died** indicates, whether the panels are reallocated between the neighbours after a cell runs out of energy.

All input parameters have default values, and are measured for a day. (The program converts these quantities for time steps. )

After inicializing the CA, one must run it step by step by

```python
c.step()
```

The results can be accessed by internal arrays of the instance:

- STAT_alloc_energy: the sum of the allocated energy per step
- STAT_alloc_panels: sum of reallocated panels
- STAT_total_active: number of active cells
- STAT_total_active_abs: absolute value of the previous variable
- STAT_total_energy: total energy of the system
- STAT_sun:
- STAT_total_production: total production
- STAT_total_consumption: total consumption
- STAT_total_alpha: total production capacity

### C++:

This multi threaded application iterates through different alpha/beta and altruism levels and writes some properties (living cells, number of clusters, size of the largest cluster and the total energy level) of the CA to files.
To run the C++ implementation of the CA, one must compile it first (three files: main.cpp, CA.h and CA.cpp). Any compiler can be used, but the std::thread library must be included. For example, in Linux:

```
g++ main.cpp CA.h CA.cpp -lpthread -o PROGRAM_NAME
```

Then it can be executed by

```
./PROGRAM_NAME n CA_grid_size initial_energy maximum_storage_capacity alpha_per_day_max days take_panels
```

where

- n: the resolution of the heatmap
- CA_grid_size: grid size of the CA (N x N)
- initial_energy: initial energy level
- maximum_storage_capacity: maximum battery level
- alpha_per_day_max: the algorthm iterates between beta/alpha = 0 to beta/alpha = alpha_per_day_max
- days: number of days to simulate, with 50 steps per day
- take_panels: reallocate solar panels or not

# Website

We also host a Github page (see link above) and the source code is availabe in the \docs folder.
