from matplotlib import pyplot as plt
import numpy as np

def average_energy(N, a, C):
    P = 0
    for i in range(0, a+1):
        P += 1/(a+1) * i
    return P - C, P

N = 50
data = np.zeros((202, 2))
i = 0
for C in [1, 100]:
    for a in range(0, 101):
        E, P = average_energy(50, a, C)
        data[i, :] = E, P/C
        i += 1

plt.scatter(data[:,1], data[:,0])
plt.show()
