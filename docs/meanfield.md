---
layout: page
title: Mean-field
permalink: /mean-field/
---


# Approach

On this page we describe our approach of the model using an approximate mean-field. In this type of system a network is generated in which each node is connected to every other node. We consider two versions of this model: 

1. Each iteration each node produces energy according to the function: randint(0, a)
2. We simulate solar days where the sun intensity is given by A * sin(2 * pi * t) for t < 1/2 and 0 otherwise. 

So let's take a look at these versions. 

# Integer Version
![placeholder](https://raw.githubusercontent.com/WavyV/Complex_System_Simulation/master/docs/pmeanfield_1.png)

![placeholder](https://raw.githubusercontent.com/WavyV/Complex_System_Simulation/master/docs/brownian_motion_meanfield.png)

![placeholder](https://raw.githubusercontent.com/WavyV/Complex_System_Simulation/master/docs/meanfield_2.png)

![placeholder](https://raw.githubusercontent.com/WavyV/Complex_System_Simulation/master/docs/deltaE_norm_dits.png)

When the system size is increased we find that the standard deviation of the distribution above decreases. This is shown in the figure below. 

![placeholder](https://raw.githubusercontent.com/WavyV/Complex_System_Simulation/master/docs/loglog_sigma_deltaE.png)


# Sine Version
We simulate the production of electricity with half a period of a sine function with amplitude A. The other half of the day, the production is zero, indicating it is night time. The consumption is constant at all times, set at C. See the figure below.

![placeholder](https://raw.githubusercontent.com/WavyV/Complex_System_Simulation/master/docs/prod_cons_functions.png)

The average amount of energy per node at time t, denoted <E(t)> is the average amount of energy per node at the previous time step plus the result of production minus consumption at the current time step. 

The total production must equal the total consumption to reach a limit cycle. In that case the integral over one day (which is one period) over the production must equal the integral over the same period for the consumption. For the functions we have chose, we find that the total production is A/pi. If consumption is equal to this, we find a limit cycle. If it is less, nodes will will experience electricity shortage and if consumption is higher, the amount of energy will keep rising. This is shown in the animations below. 

Production equals consumption.
<iframe width="560" height="315" src="https://www.youtube.com/embed/SkG6L0Pgsqc" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>

Consumption is less than production.
<iframe width="560" height="315" src="https://www.youtube.com/embed/MlCKcaE2XBo" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>

Consumption is more than production.
<iframe width="560" height="315" src="https://www.youtube.com/embed/ZZ1x-JXrv7U" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>

To see the effect of the maximum battery capacity we can set the capacity such that the batteries will be completely filled during the day. If the capacity is too low, the nodes may not survive the night. 

<iframe width="560" height="315" src="https://www.youtube.com/embed/M6HUZ-9DL4s" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>

We have investigated the dynamics of this simple model version and gotten a feel for how the model behaves. This will help us understand the more complicated dynamics observed for the more advanced cellular automata and network model implementations. 
