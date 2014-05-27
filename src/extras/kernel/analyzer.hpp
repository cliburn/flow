#ifndef ANALYZER_HPP
#define ANALYZER_HPP

#include "common.hpp"

class Analyzer 
{
public:
  Analyzer(vector<vector<double> > _data, int _dim, int _n, int _k, double _h, double _alpha);
  Analyzer(const Analyzer &a);
  Analyzer& operator=(const Analyzer &rhs);
  virtual ~Analyzer();
  vector<int> find_seeds(double radius, int min_nbrs, int max_seeds);
  vector<int> find_seeds_simple(int max_seeds);
  virtual vector<double> mean_shift(vector<double> x) = 0;
  // vector<double> mean_shift_uniform(vector<double> x);
  // vector<double> mean_shift_epanechnikov(vector<double> x);
  virtual double density(vector<double> x) = 0;
  // double density_epanechnikov(vector<double> x);
  // double density_uniform(vector<double> x);
  bool dip_test(vector<double> m1, vector<double> m2, double dip_ratio);
  // bool dip_test_epanechnikov(vector<double> m1, vector<double> m2, double dip_ratio);
  map<int, vector<double> > find_modes(vector<int> seeds, double eps);
  // map<int, vector<double> > find_modes_epanechnikov(vector<int> seeds, double eps);
  double norm(vector<double> x);
  double euclid_dist(vector<double> x1, vector<double> x2);
  map<vector<double>, vector<int> > merge_modes(map<int, vector<double> > m, double min_sep);
  vector<int> find_nbrs(vector<double> x, int k);
  map<vector<double>, vector<int> > check_modes(map<vector<double>, vector<int> > m, double dip_ratio);
  // map<vector<double>, vector<int> > check_modes_epanechnikov(map<vector<double>, vector<int> > m, double dip_ratio);
  map<vector<double>, vector<int> > pop_check_modes(map<vector<double>, vector<int> > m, unsigned min_pop);
  double get_h();
  void set_h(double h);
  double calc_h(); // automatically calculate an 'optimal' value for h from data

protected:
  ANNpointArray data;
  ANNidxArray idx;
  ANNdistArray dist;
  ANNkd_tree* tree;
  int dim;
  int n;
  int k;
  double h;
  double alpha;
};

class Uniform_Analyzer : public Analyzer
{
public:
  Uniform_Analyzer(vector<vector<double> > _data, int _dim, int _n, int _k, double _h, double _alpha);
  vector<double> mean_shift(vector<double> x);
  double density(vector<double> x);
};

class Epanechnikov_Analyzer : public Analyzer
{
public:
  Epanechnikov_Analyzer(vector<vector<double> > _data, int _dim, int _n, int _k, double _h, double _alpha);
  vector<double> mean_shift(vector<double> x);
  double density(vector<double> x);
};

#endif
