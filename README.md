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

Python:
- Open cellular_automata.py
- Set the preferred parameters
- Execute the code

C++:
This program iterates through different alpha/beta and altruism levels and writes some properties (living cells, number of clusters, size of the largest cluster and the total energy level) of the CA to files. 
- To run the C++ implementation of the CA, one must compile it first (three files: main.cpp, CA.h and CA.cpp). Any compiler can be used, but the std::thread library must be included. For example, in Linux:
g++ main.cpp CA.h CA.cpp -lpthread -o PROGRAM_NAME
Then it can be executed by 
./PROGRAM_NAME n CA_grid_size initial_energy maximum_storage_capacity alpha_per_day_max days take_panels
where
n: the resolution of the heatmap
CA_grid_size: grid size of the CA (N x N)
initial_energy: initial energy level
maximum_storage_capacity: maximum battery level
alpha_per_day_max: the algorthm iterates between beta/alpha = 0 to beta/alpha = alpha_per_day_max
days: number of days to simulate, with 50 steps per day
take_panels: reallocate solar panels or not

# Website

We also host a Github page (see link above) and the source code is availabe in the \docs folder.
