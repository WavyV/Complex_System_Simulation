---
layout: page
title: Cellular Automata
permalink: /cellular/
---

On this page we will describe our approach of the model on a cellular automaton. For a small introduction to cellular automat, please read: http://mathworld.wolfram.com/CellularAutomaton.html

# Approach

For this 2D cellular automaton, we used a N x N grid, where each cell is able to produce and consume electricity. We define the production per cell as $p(t) = max(A sin(2 \pi t) ,0)$, where $A~U[0,1]$ over all cells, while the consumption is a constant factor \beta.

| name  | greek    |
|-------|----------|
| alpha | $\alpha$ |
| beta  | $\beta$  |
| gamma | $\gamma$ |
| delta | $\delta$ |

# Results

<iframe width="560" height="315" src="https://www.youtube.com/embed/lQolYLWnwS8" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
