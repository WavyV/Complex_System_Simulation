


#ifndef CA_H_
#define CA_H_

class CA {
	int n;
	float dt;
	float energy_start;
	float beta_per_step;


	float energy_max;
	float energy_min;
	bool take_panels;


	float* temp;
	float* energy;
	int* friend_n;

	float t;
	int step_num;


	void count_neighbours();
	void produce_energy();
	void get_energy();
	void consume();
	void get_panels();

	void print_array(float* array);
	void print_array(int* array);
public:
	float* alpha;
	// STAT
	float STAT_energy;
	int STAT_living;
	int STAT_numshapes;
	int STAT_maxsize;
	float STAT_total_production;
	float STAT_total_consumption;


	CA(int n, int step_per_day, float energy_start, float alpha_per_day, float beta_per_day, float energy_max, float energy_min, bool take_panels);
	virtual ~CA();
	void step();
	void run(int days);


	void count_living();
	void sum_energy();
	void count_shapes();

	void print_alpha()
	{
		this->print_array(this->alpha);
	}
	void print_energy()
	{
		this->print_array(this->energy);
	}
};


class coord
{
public:
	int coord_i;
	int coord_j;
};


#endif
