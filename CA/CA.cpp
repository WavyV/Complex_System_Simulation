/*
 * CA.cpp
 *
 *  Created on: Jun 20, 2018
 *      Author: gregory
 */

#include "CA.h"
#include <string.h>
#include <math.h>
#include <algorithm>
#include <random>

CA::CA(int n, float dt, float energy_start, float alpha_min, float alpha_max, float beta, float energy_max, float energy_min, bool take_panels)
{
	// Set parameters
	this->n = n;
	this->dt = dt;
	this->energy_start = energy_start;
	this->alpha_min = alpha_min;
	this->alpha_max = alpha_max;
	this->beta = beta;
	this->energy_max = energy_max;
	this->energy_min = energy_min;
	this->take_panels = take_panels;


	this->alpha = new float[(this->n)*(this->n)];
	memset(this->alpha, 0, (this->n)*(this->n)*sizeof(float));

	// Set random numbers
	std::random_device rd;  //Will be used to obtain a seed for the random number engine
	std::mt19937 gen(rd()); //Standard mersenne_twister_engine seeded with rd()
	std::uniform_real_distribution<double> dis(this->alpha_min, this->alpha_max);

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


	// STAT
	this->count_living();
	this->sum_energy();
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
	double x;
	int index;
	x = this->t - ((int)this->t);

	if(x<0.5)
	{
		for(int i=1; i<(this->n)-1; i=i+1)
		{
			for(int j=1; j<(this->n)-1; j=j+1)
			{
				index = i*(this->n)+j;
				this->energy[index] += this->alpha[index]*sin(2*M_PI*x);
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

			this->energy[index] = this->energy[index] - this->beta;
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

void CA::get_panels()
{
	// Get panels from neighbours, if it is allowed
	int index;
	if(this->take_panels)
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
					this->alpha[index] += this->temp[(i-1)*(this->n)+j] +
											this->temp[(i+1)*(this->n)+j] +
											this->temp[i*(this->n)+j-1] +
											this->temp[i*(this->n)+j+1];
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


