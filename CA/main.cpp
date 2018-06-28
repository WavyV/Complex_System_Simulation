#include <iostream>
#include "CA.h"
#include <stdlib.h>
#include <fstream>
#include <string>
#include <thread>


void worker(int id,
			int n_threads,
			float* result_energy,
			float* result_living,
			float *result_numshape,
			float* result_maxsize,
			int result_n,
			float days,
			int n,
			float step_per_day,
			float energy_start,
			float* alpha_per_day,
			float beta_per_day,
			float energy_max,
			float* energy_min,
			bool take_panels)
{
	for(int i=id; i<result_n; i=i+n_threads)
	{
		CA c(n,
			step_per_day,
			energy_start,
			alpha_per_day[i],
			beta_per_day,
			energy_max,
			energy_min[i],
			take_panels);

			c.run(days);

			c.count_living();
			c.sum_energy();
			c.count_shapes();

			result_living[i] = c.STAT_living;
			result_energy[i] = c.STAT_energy;
			result_numshape[i] = c.STAT_numshapes;
			result_maxsize[i] = c.STAT_maxsize;

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
/*
	// n, step/day, energy_start, alpha_per_day, beta_per_day, energy_max, energy_min, take_panels
	CA c(	8, // n
			50, // step/day
			0.01, // energy0
			0.01, // alpha
			1.0, // beta
			100.0, // energy max
			100.0, // energy min
			true); // take panel
	c.alpha[1*8+1] = 0.5;
	c.alpha[2*8+1] = 0.1;
	c.alpha[1*8+2] = 0.1;
	for(int i=0; i<1000; i=i+1)
	{
		c.step();
	}
	c.count_living();
	std::cout << c.STAT_living << std::endl;
	c.print_energy();
*/


	if(argc < 7)
	{
		std::cout << "Please specify all imput parameters!\n";
		std::cout << "n, CA_grid_size, energy_start, energy_max, alpha_per_day_max, days, take_panels\n";
		return 0;
	}


	// Model parameters
	int n = atoi(argv[1]);
	printf("Resolution: %d x %d\n", n, n);

	int CA_grid_size = atoi(argv[2]);
	printf("CA grid size %d x %d\n", CA_grid_size, CA_grid_size);

	float energy_start = atof(argv[3]);
	printf("Initial energy: %lf\n", energy_start);

	float energy_max = atof(argv[4]);
	printf("Maximum storage capacity: %lf\n", energy_max);

	float alpha_per_day_max = atof(argv[5]);
	printf("Production / day: %lf\n", alpha_per_day_max);

	int days = atoi(argv[6]);
	printf("Number of days: %d\n", days);

	bool take_panels = (atoi(argv[7])==1);
	printf("Taking panels: %d\n", take_panels);


	int step_per_day = 50;
	float beta_per_day = 1.0;

	// Contaners for input parameters
	float* alpha_per_day = new float[n*n];
	float* energy_min = new float[n*n];

	// Containers for the results
	float* result_energy = new float[n*n];
	float* result_living = new float[n*n];
	float* result_numshape = new float[n*n];
	float* result_maxsize = new float[n*n];

	// Fill up input parameter vectors
	int index;
	for(int i=0; i<n; i=i+1)
	{
		for(int j=0; j<n; j=j+1)
		{
			index = i*n+j;
			alpha_per_day[index] = 5.0; //alpha_per_day_max/n*i;
			energy_min[index] = energy_max/n*j;
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
									std::ref(result_numshape),
									std::ref(result_maxsize),
									n*n,
									days,
									CA_grid_size,
									step_per_day,
									energy_start,
									std::ref(alpha_per_day),
									beta_per_day,
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
	std::ofstream file_energy, file_living, file_numshape, file_maxsize;
	file_energy.open("energy_alpha5.csv");
	file_living.open("living_alpha5.csv");
	file_numshape.open("numshape_alpha5.csv");
	file_maxsize.open("maxsize_alpha5.csv");

	for(int i=0; i<n; i=i+1)
	{
		for(int j=0; j<n; j=j+1)
		{
			file_living << result_living[i*n+j] << ",";
			file_energy << result_energy[i*n+j] << ",";
			file_numshape << result_numshape[i*n+j] << ",";
			file_maxsize << result_maxsize[i*n+j] << ",";
		}
		file_energy << std::endl;
		file_living << std::endl;
		file_numshape << std::endl;
		file_maxsize << std::endl;
	}
	file_energy.close();
	file_living.close();
	file_numshape.close();
	file_maxsize.close();

	std::cout << "\n";
	std::cout.flush();
	std::cout << "Simulation finished successfully.\n";

	// Imshow
	//std::string command = "python plot_result.py";
	//system(command.c_str());
// */
	return 0;
}

