import matplotlib.pyplot as plt
import numpy
import pandas

living = pandas.read_csv('living.csv', header=None)
energy = pandas.read_csv('energy.csv', header=None)

living = living.values[:, 0:-2]
energy = energy.values[:, 0:-2]

living[living==0] = numpy.nan
energy[energy==0] = numpy.nan

plt.figure(figsize=[8, 3])

plt.subplot(1, 3, 1)
plt.pcolor(living, vmin=0)
plt.ylabel('Alpha_max')
plt.xlabel('Energy_min / Energy_max [%]')
plt.title('Living')
plt.colorbar()

plt.subplot(1, 3, 2)
plt.pcolor(energy)
plt.ylabel('Alpha_max')
plt.xlabel('Energy_min / Energy_max [%]')
plt.title('Energy')
plt.colorbar()

plt.subplot(1, 3, 3)
plt.pcolor(energy/living)
plt.ylabel('Alpha_max')
plt.xlabel('Energy_min / Energy_max [%]')
plt.title('Energy/Living')
plt.colorbar()

plt.tight_layout()

plt.show()

