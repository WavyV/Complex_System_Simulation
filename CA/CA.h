


#ifndef CA_H_
#define CA_H_

class CA {
	int n;
	float dt;
	float energy_start;
	float alpha_min;
	float alpha_max;
	float beta;
	float energy_max;
	float energy_min;
	bool take_panels;

	float* alpha;
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

	// STAT
	float STAT_energy;
	int STAT_living;


	CA(int n, float dt, float energy_start, float alpha_min, float alpha_max, float beta, float energy_max, float energy_min, bool take_panels);
	virtual ~CA();
	void step();


	void count_living();
	void sum_energy();
};

#endif
