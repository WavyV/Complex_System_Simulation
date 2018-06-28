
#include "CA.h"
#include <string.h>
#include <math.h>
#include <algorithm>
#include <random>
#include <iostream>


CA::CA(	int n,
		int step_per_day,
		float energy_start,
		float alpha_per_day,
		float beta_per_day,
		float energy_max,
		float energy_min,
		bool take_panels)
{
	// Set parameters
	this->n = n;
	this->dt = 1.0/step_per_day;
	this->energy_start = energy_start;
	this->beta_per_step = beta_per_day / step_per_day;
	this->energy_max = energy_max;
	this->energy_min = energy_min;
	this->take_panels = take_panels;



	this->alpha = new float[(this->n)*(this->n)];
	memset(this->alpha, 0, (this->n)*(this->n)*sizeof(float));

	// Set random numbers
	std::random_device rd;
	std::mt19937 gen(rd());
	std::uniform_real_distribution<double> dis(0.0, 2.0*alpha_per_day/0.31831/step_per_day);

	this->energy = new float[(this->n)*(this->n)];
	memset(this->energy, 0, ((this->n)*(this->n))*sizeof(float));

	int index;
	for (int i=1; i<(this->n)-1; i=i+1)
	{
		for(int j=1; j<(this->n)-1; j=j+1)
		{
			index = i*(this->n)+j;
			this->alpha[index] = dis(gen);

			this->energy[index] = this->energy_start;
		}
	}

	this->temp = new float[(this->n)*(this->n)];
	memset(this->temp, 0, ((this->n)*(this->n))*sizeof(float));

	this->friend_n = new int[(this->n)*(this->n)];
	memset(this->friend_n, 0, ((this->n)*(this->n))*sizeof(float));

	this->t = 0;
	this->step_num = 0;

	// STAT
	this->STAT_living = 0;
	this->STAT_energy = 0;
	this->STAT_numshapes = 0;
	this->STAT_maxsize = 0;
	this->STAT_total_production = 0;
	this->STAT_total_consumption = 0;
}

CA::~CA() {
	// TODO Auto-generated destructor stub
	delete 	alpha;
	delete temp;
	delete energy;
}

void CA::step()
{
	// Increase time
	this->step_num++;
	this->t += this->dt;

	// Count living neighbours
	this->count_neighbours();

	// Produce energy
	this->produce_energy();

	// Allocate energy
	this->get_energy();

	// Consume energy
	this->consume();

	// Allocate panels
	this->get_panels();

}


void CA::run(int days)
{
	float num_steps = days / this->dt;
	for(int i=0; i<num_steps;i=i+1)
	{
		this->step();
	}

	this->count_shapes();
	this->sum_energy();
	this->count_living();
}



void CA::count_neighbours()
{
	// Count the number of neighbours and put this number to an array
	for(int i=1; i<(this->n)-1; i=i+1)
	{
		for(int j=1; j<(this->n)-1; j=j+1)
		{
			this->friend_n[i*(this->n)+j] = (this->energy[(i-1)*(this->n)+j]>0) +
									(this->energy[(i+1)*(this->n)+j]>0) +
									(this->energy[i*(this->n)+j-1]>0) +
									(this->energy[i*(this->n)+j+1]>0);
		}
	}
}

void CA::produce_energy()
{
	// Adds energy based on alpha
	double prod = 0, x = this->t - ((int)this->t);
	int index;

	if(x<0.5)
	{
		for(int i=1; i<(this->n)-1; i=i+1)
		{
			for(int j=1; j<(this->n)-1; j=j+1)
			{
				index = i*(this->n)+j;
				prod = this->alpha[index]*sin(2*M_PI*x);
				this->energy[index] += prod;
				this->STAT_total_production += prod;



				if(this->energy[index]>this->energy_max)
				{
					this->energy[index] = this->energy_max;
				}
			}
		}
	}
}


void CA::get_energy()
{
	// Get energy from neighbours

	// Calculate energy that can be given to neighbours
	double sharable;
	int index;
	for(int i=1; i<(this->n)-1; i=i+1)
	{
		for(int j=1; j<(this->n)-1; j=j+1)
		{
			index = i*(this->n)+j;

			sharable = this->energy[index]-this->energy_min;
			if(sharable < 0)
			{
				sharable = 0;
			}


			if(this->friend_n[index]>0)
			{
				this->temp[index] = sharable / (float)this->friend_n[index];
				//this->energy[index] = this->energy[index] - sharable;
			}
			else
			{
				this->temp[index] = 0.0;
			}
		}
	}

	// Get energy from neighbours
	for(int i=1; i<(this->n)-1; i=i+1)
	{
		for(int j=1; j<(this->n)-1; j=j+1)
		{
			index = i*(this->n)+j;

			if(this->energy[index] > 0)
			{
				this->energy[index] += this->temp[(i-1)*(this->n)+j] +
										this->temp[(i+1)*(this->n)+j] +
										this->temp[i*(this->n)+j-1] +
										this->temp[i*(this->n)+j+1] - this->temp[index]*this->friend_n[index];

			}

		}
	}

	//this->print_array(this->energy);


}

void CA::consume()
{
	// Decrease energy amount
	int index;
	for(int i=1; i<(this->n)-1; i=i+1)
	{
		for(int j=1; j<(this->n)-1; j=j+1)
		{
			index = i*(this->n)+j;
			if(this->energy[index] > 0)
			{
				this->energy[index] = this->energy[index] - this->beta_per_step;
				this->STAT_total_consumption += this->beta_per_step;

				// Energy must be in [0, energy_max]
				if(this->energy[index]<0)
				{
					this->energy[index] = 0;
				}
				if(this->energy[index]>this->energy_max)
				{
					this->energy[index] = this->energy_max;
				}
			}
		}
	}
}

void CA::get_panels()
{
	// Neighbours must be counted again
	this->count_neighbours();

	// Get panels from neighbours, if it is allowed
	int index;
	double panel_taken = 0;
	if((int)this->take_panels>0)
	{

		for(int i=1; i<(this->n)-1; i=i+1)
		{
			for(int j=1; j<(this->n)-1; j=j+1)
			{
				index = i*(this->n)+j;

				if((this->energy[index]==0) && (this->friend_n[index]>0))
				{
					this->temp[index] = this->alpha[index] / (float)this->friend_n[index];
				}
				else
				{
					this->temp[index] = 0.0;
				}
			}
		}

		// Get alpha from neighbours
		for(int i=1; i<(this->n)-1; i=i+1)
		{
			for(int j=1; j<(this->n)-1; j=j+1)
			{
				index = i*(this->n)+j;
				if(this->energy[index] > 0)
				{
					panel_taken = this->temp[(i-1)*(this->n)+j] +
											this->temp[(i+1)*(this->n)+j] +
											this->temp[i*(this->n)+j-1] +
											this->temp[i*(this->n)+j+1];
					this->alpha[index] += panel_taken;
				}
			}
		}
	}

	// Non operating cells has alpha = 0
	for(int i=1; i<(this->n)-1; i=i+1)
	{
		for(int j=1; j<(this->n)-1; j=j+1)
		{
			index = i*(this->n)+j;
			if(this->energy[index] == 0)
			{
				this->alpha[index] = 0;
			}
		}
	}



}



void CA::count_living()
{
	int num = 0;

	for(int i=1; i<(this->n)-1; i=i+1)
	{
		for(int j=1; j<(this->n)-1; j=j+1)
		{
			num += (this->energy[i*(this->n)+j] > 0);
		}
	}

	this->STAT_living = num;
}

void CA::sum_energy()
{
	float num = 0;

	for(int i=1; i<(this->n)-1; i=i+1)
	{
		for(int j=1; j<(this->n)-1; j=j+1)
		{
			num += this->energy[i*(this->n)+j];
		}
	}

	this->STAT_energy = num;
}



void CA::count_shapes()
{
	int index, size=0, proc_index = 0;
	int numshape = 0;
	int maxsize = 0;

	coord* c = new coord[this->n*this->n];

	for(int i=1; i<this->n-1; i=i+1)
	{
		for(int j=1; j<this->n-1; j=j+1)
		{
			index = i*this->n+j;
			this->temp[index] = (this->energy[index]>0);
		}
	}

	for(int i=1; i<this->n-1; i=i+1)
	{
		for(int j=1; j<this->n-1; j=j+1)
		{


			if(this->temp[i*this->n+j]==1)
			{
				// Add the first cell
				c[size].coord_i = i;
				c[size].coord_j = j;

				// Increment size
				size = 1;
				proc_index = 0;

				// Set corresponting cell to 0
				this->temp[i*this->n+j] = 0;

				//printf("Cell (%d, %d) added.\n", i, j);

				while(proc_index <= size)
				{
					//printf("Processing (%d, %d)\n", c[proc_index].coord_i, c[proc_index].coord_j);

					index = (c[proc_index].coord_i+1)*this->n+(c[proc_index].coord_j);
					if(this->temp[index]==1)
					{
						this->temp[index] = 0;
						c[size].coord_i = c[proc_index].coord_i+1;
						c[size].coord_j = c[proc_index].coord_j;
						size++;

						//printf("Neighbour found at (%d, %d)\n", c[size-1].coord_i, c[size-1].coord_j);
					}

					index = (c[proc_index].coord_i-1)*this->n+(c[proc_index].coord_j);
					if(this->temp[index]==1)
					{
						this->temp[index] = 0;
						c[size].coord_i = c[proc_index].coord_i-1;
						c[size].coord_j = c[proc_index].coord_j;
						size++;
						//printf("Neighbour found at (%d, %d)\n", c[size-1].coord_i, c[size-1].coord_j);
					}

					index = (c[proc_index].coord_i)*this->n+(c[proc_index].coord_j+1);
					if(this->temp[index]==1)
					{
						this->temp[index] = 0;
						c[size].coord_i = c[proc_index].coord_i;
						c[size].coord_j = c[proc_index].coord_j+1;
						size++;
						//printf("Neighbour found at (%d, %d)\n", c[size-1].coord_i, c[size-1].coord_j);
					}

					index = (c[proc_index].coord_i)*this->n+(c[proc_index].coord_j-1);
					if(this->temp[index]==1)
					{
						this->temp[index] = 0;
						c[size].coord_i = c[proc_index].coord_i;
						c[size].coord_j = c[proc_index].coord_j-1;
						size++;
						//printf("Neighbour found at (%d, %d)\n", c[size-1].coord_i, c[size-1].coord_j);
					}

					proc_index++;
				}
				//printf("Shape found with size: %d\n", size);
				numshape++;
				if(maxsize < size)
				{
					maxsize = size;
				}
			}

		}
	}
	this->STAT_maxsize = maxsize;
	this->STAT_numshapes = numshape;
}



void CA::print_array(float* array)
{
	printf("\n\n");
	printf("-------------------------\n");
	for(int i=0; i<this->n; i=i+1)
	{
		for(int j=0; j<this->n; j=j+1)
		{
			printf("%04.2f   ", array[i*(this->n)+j]);
		}
		printf("\n");
	}
	printf("-------------------------\n");
}

void CA::print_array(int* array)
{
	printf("\n\n");
	printf("-------------------------\n");
	for(int i=0; i<this->n; i=i+1)
	{
		for(int j=0; j<this->n; j=j+1)
		{
			printf("%d   ", array[i*(this->n)+j]);
		}
		printf("\n");

	}
	printf("-------------------------\n");
}


