#include <iostream>
#include "CA.h"
#include <stdlib.h>
#include <fstream>
#include <string>
#include <thread>

void print_array(float* array, int n)
{
	printf("\n\n");
	printf("-------------------------\n");
	for(int i=0; i<n; i=i+1)
	{
		for(int j=0; j<n; j=j+1)
		{
			printf("%04.2f   ", array[i*(n)+j]);
		}
		printf("\n");
	}
	printf("-------------------------\n");
}


void worker(int id,
			int n_threads,
			float* result_energy,
			float* result_living,
			int result_n,
			int n,
			float dt,
			float energy_start,
			float alpha_min,
			float* alpha_max,
			float beta,
			float energy_max,
			float* energy_min,
			bool take_panels)
{
	for(int i=id; i<result_n; i=i+n_threads)
	{
		CA c(n, 			// n
			dt, 			// dt
			energy_start, 	// energy_start
			alpha_min, 		// alpha_min
			alpha_max[i], 	// alpha_max
			beta, 			// beta
			energy_max,		// energy_max
			energy_min[i], 	// energy_min
			take_panels);	// take_panels

			for(int k=0; k<200; k=k+1)
			{
				c.step();
			}
			result_living[i] = c.STAT_living;
			result_energy[i] = c.STAT_energy;

			if(id==0)
			{
				int num =(double)30/result_n*i;
				std::cout << "Process: [";
				for(int m=0; m<30;m=m+1)
				{
					if(m<=num)
					{
						std::cout << "#";
					}
					else
					{
						std::cout << " ";
					}
				}
				std::cout << "]" << "\r";
				std::cout.flush();
			}

	}

}




int main(int argc, char* argv[])
{
	if(argc < 4)
	{
		std::cout << "Please specify all imput parameters!\n";
		std::cout << "n, energy_start, energy_max, alpha_max\n";
		return 0;
	}


	int n = atoi(argv[1]);

	float* result_energy = new float[n*n];
	float* result_living = new float[n*n];

	float dt = 0.01;
	float energy_start = atof(argv[2]);
	float alpha_min = 0;
	float* alpha_max = new float[n*n];
	float beta = 1;
	float energy_max = atof(argv[3]);
	float* energy_min = new float[n*n];
	bool take_panels = true;


	float alpha_max_min = 0;
	float alpha_max_max = atof(argv[4]);
	float energy_min_min = 0;
	float energy_min_max = energy_max;

	std::cout << "Grid: " << n << " by " << n << std::endl;
	std::cout << "Initial energy: " << energy_start << std::endl;
	std::cout << "Maximum energy level: " << energy_max << std::endl;
	std::cout << "Alpha max: " << alpha_max_max << std::endl;

	float a, e;
	int index;
	for(int i=0; i<n; i=i+1)
	{
		for(int j=0; j<n; j=j+1)
		{
			index = i*n+j;
			a = alpha_max_min + 1.0*(alpha_max_max-alpha_max_min)/n*i;
			e = energy_min_min + 1.0*(energy_min_max-energy_min_min)/n*j;
			alpha_max[index] = a;
			energy_min[index] = e;
		}
	}


	int n_threads = std::thread::hardware_concurrency();
	std::thread *threads = new std::thread[n_threads];
	for(int i=0; i<n_threads; i=i+1)
	{
		threads[i] = std::thread(	worker,
									i,
									n_threads,
									std::ref(result_energy),
									std::ref(result_living),
									n*n,
									n,
									dt,
									energy_start,
									alpha_min,
									std::ref(alpha_max),
									beta,
									energy_max,
									std::ref(energy_min),
									take_panels);

	}

	// Join the threads
	for(int i=0; i<n_threads; i=i+1)
	{
		threads[i].join();
	}

	// Write to file
	std::ofstream file_energy, file_living;
	file_energy.open("energy.csv");
	file_living.open("living.csv");

	for(int i=0; i<n; i=i+1)
	{
		for(int j=0; j<n; j=j+1)
		{
			file_living << result_living[i*n+j] << ",";
			file_energy << result_energy[i*n+j] << ",";
		}
		file_energy << std::endl;
		file_living << std::endl;
	}
	file_energy.close();
	file_living.close();

	std::cout << "\n";
	std::cout.flush();
	std::cout << "Simulation finished successfully.\n";

	// Imshow
	std::string command = "python plot_result.py";
	system(command.c_str());

	return 0;
}

