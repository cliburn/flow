#include "analyzer.hpp"
#include "Python.h"

#ifdef _MSC_VER
inline int round(double x)
{
return int(x > 0.0 ? x + 0.5 : x - 0.5);
}
#endif

Analyzer::Analyzer(vector<vector<double> > _data, int _dim, int _n, int _k, double _h=0, double _alpha=0): 
  dim(_dim), n(_n), k(_k), h(_h), alpha(_alpha)
  // constructor for finding modes in flow data
{
  data = annAllocPts(n, dim);
  for (int i=0; i<n; ++i) {
    for (int j=0; j<dim; ++j) {
      data[i][j] = _data[i][j];
    }
  }

  idx = new ANNidx[k];
  dist = new ANNdist[k];
  tree = new ANNkd_tree(data, n, dim);

  if (h == 0) {
    h = calc_h();
  }
}


Analyzer::Analyzer(const Analyzer &a):
  // copy constructor
  data(a.data), dim(a.dim), n(a.n), k(a.k) 
{
  idx = new ANNidx[k];
  dist = new ANNdist[k];
  tree = new ANNkd_tree(data, n, dim);
}

Analyzer& Analyzer::operator=(const Analyzer &rhs)
  // assignment operator
{
  if (&rhs != this) {
    delete [] idx;
    delete [] dist;
    delete tree;
    annDeallocPts(data);
    idx = new ANNidx[rhs.k];
    dist = new ANNdist[rhs.k];
    tree = new ANNkd_tree(rhs.data, rhs.n, rhs.dim);
  }
  return *this;
}

Analyzer::~Analyzer() 
  // destructor
{
  delete [] idx;
  delete [] dist;
  delete tree;
  annDeallocPts(data);
}

vector<int> Analyzer::find_seeds_simple(int max_seeds)
  // returns max_seeds at randomly chosen points
{
  // Py_BEGIN_ALLOW_THREADS
  vector<int> seed_idx(n);
  for (int i=0; i<n; ++i) {
    seed_idx[i] = i;
  }
  random_shuffle(seed_idx.begin(), seed_idx.end());

  vector<int> seeds(seed_idx.begin(), seed_idx.begin()+max_seeds);
  return seeds;
  // Py_END_ALLOW_THREADS
}

vector<int> Analyzer::find_seeds(double radius, int min_nbrs, int max_seeds) 
  // returns seeds which are at least radius separated and with >= min_nbrs
{
  // Py_BEGIN_ALLOW_THREADS
  set<int> seen;

  if (max_seeds == 0) {
    max_seeds = (int) sqrt(float(n));
  }
  if (max_seeds > k) {
    max_seeds = k;
  }
  vector<int> seed_idx(n);
  for (int i=0; i<n; ++i) {
    seed_idx[i] = i;
  }
  random_shuffle(seed_idx.begin(), seed_idx.end());

  vector<int> seeds;
  //! change so that will return max_seeds number of seeds
  int total = 0;
  for (int i=0; i<n; ++i) {
    if (seen.count(seed_idx[i]) == 0) {
      int num = min(k, tree->annkFRSearch(data[seed_idx[i]], radius*radius, k, idx, dist, alpha));
      if (num >= min_nbrs) {
	seeds.push_back(seed_idx[i]);
	total++;
	if (total >= max_seeds) break; // only find as many seeds as requested
      }
      // put all nbrs within radius of seed in seen list so as not to choose them as seeds in future
      vector<int> nbrs(idx, idx+num);
      seen.insert(nbrs.begin(), nbrs.end());
    }
    
    /* OLD CODE
      for (int i=0; i<max_seeds; ++i) {
    // int ii = seed_idx[i] - 1;
    if (seen.count(seed_idx[i]) == 0) {
      int num = min(k, tree->annkFRSearch(data[seed_idx[i]], radius*radius, k, idx, dist, alpha));
      if (num >= min_nbrs) {
	seeds.push_back(seed_idx[i]);
      }
      // put all nbrs within radius of seed in seen list so as not to choose them as seeds in future
      vector<int> nbrs(idx, idx+num);
      seen.insert(nbrs.begin(), nbrs.end());
    }
    */
  }
  return seeds;
  // Py_END_ALLOW_THREADS
}

bool Analyzer::dip_test(vector<double> m1, vector<double> m2, double dip_ratio)
  // returns true if a valley lies between m1 and m2, false otherwise
{
  // Py_BEGIN_ALLOW_THREADS
  double m = min(density(m1), density(m2));
  vector<vector<double> > stepset;
  for (int d=0; d<dim; ++d) {
    vector<double> steps(9, 0.0);
    double start = m1[d];
    double stop = m2[d];
    bool toReverse = false;
    if (start > stop) {
      double tmp = stop;
      stop = start;
      start = tmp;
      toReverse = true;
    }
    double current = start;
    double step = (stop-start)/10;
    for (int i=0; i<9; ++i) {
      current += step;
      steps[i] = current;
    }
    if (toReverse) {
      reverse(steps.begin(), steps.end());
    }
    stepset.push_back(steps);
  }

  vector<double> x(dim, 0.0);
  vector<double> dens;
  for (unsigned i=0; i<stepset[0].size(); ++i) {
    for (int d=0; d<dim; ++d) {
      x[d] = stepset[d][i];
    }
    double d = density(x);
    dens.push_back(d);
  }
  double mm = *min_element(dens.begin(), dens.end());
  if (mm/m < dip_ratio) {
    return true;
  } else {
    return false;
  }
  // Py_END_ALLOW_THREADS
}

double Analyzer::norm(vector<double> x) {
  // returns L2 norm
  double result = 0;
  for (unsigned i=0; i<x.size(); ++i) {
    result += x[i]*x[i];
  }
  return sqrt(result);
}

double Analyzer::euclid_dist(vector<double> x1, vector<double> x2) {
  // returns euclidean distance between two points 
  vector<double> delta;
  for (unsigned i=0; i<x1.size(); ++i) {
    delta.push_back(x1[i] - x2[i]);
  }
  return norm(delta);
}

map<int, vector<double> > Analyzer::find_modes(vector<int> seeds, double eps) 
  // returns modes found with epanechnikov kernel
{
  map<int, vector<double> > m;
  Py_BEGIN_ALLOW_THREADS
  for (unsigned i=0; i<seeds.size(); ++i) {
    vector<double> x(data[seeds[i]], data[seeds[i]]+dim);
    vector<double> delta(dim, 1e6);
    while (norm(delta) > eps) {
      delta = mean_shift(x);
      for (int d=0; d<dim; ++d) {
	x[d] += delta[d];
      }
    }
    m[seeds[i]] = x;
  }
  Py_END_ALLOW_THREADS
  return m;
}

map<vector<double>, vector<int> > Analyzer::pop_check_modes(map<vector<double>, vector<int> > m, unsigned min_pop=1)
  // returns modes with at >= min_pop starters
{
  // Py_BEGIN_ALLOW_THREADS
  if (min_pop == 1) {
    return m;
  }
  else {
    map<vector<double>, vector<int> > good_modes;
    map<vector<double>, vector<int> >::iterator it;
    for (it=m.begin(); it!=m.end(); ++it) {
      if ((it->second).size() >= min_pop) {
	good_modes[it->first] = it->second;
      }
    }
    return good_modes;
  }
  // Py_END_ALLOW_THREADS
}

map<vector<double>, vector<int> > Analyzer::check_modes(map<vector<double>, vector<int> > m, double dip_ratio)
  // returns modes with a dip of at least dip_ratio on curve between them
  // otherwise throws away mode with lower density
{
  // Py_BEGIN_ALLOW_THREADS
  set<vector<int> > bad_seeds;
  map<vector<double>, vector<int> > good_modes;
  map<vector<double>, vector<int> >::iterator it1;
  map<vector<double>, vector<int> >::iterator it2;
  for (it1=m.begin(); it1!=m.end(); ++it1) {
    for (it2=it1; it2!=m.end(); ++it2) {
      if (it1 != it2 && !(dip_test(it1->first, it2->first, dip_ratio))) {
	double d1 = density(it1->first);
	double d2 = density(it2->first);
	if (d1 < d2) {
	  bad_seeds.insert(it1->second);
	} else {
	  bad_seeds.insert(it2->second);
	}
      }
    }
  }
  for (it1=m.begin(); it1!=m.end(); ++it1) {
    if (bad_seeds.count(it1->second) == 0) {
      good_modes[it1->first] = it1->second;
    }
  }
  return good_modes;
  // Py_END_ALLOW_THREADS
}

map<vector<double>, vector<int> > Analyzer::merge_modes(map<int, vector<double> > m, double min_sep)
// merge modes that are separated by < min_sep in each dimension
{
  // Py_BEGIN_ALLOW_THREADS

  map<vector<double>, vector<int> > modes;
  map<int, vector<double> >::iterator map_it;
  for (map_it=m.begin(); map_it!=m.end(); ++map_it) {
    vector<double> v = map_it->second;

    for (unsigned i=0; i<v.size(); ++i) {
      v[i] = min_sep*round(v[i]/min_sep);
    }
    modes[v].push_back(map_it->first);
  }
  return modes;
  // Py_END_ALLOW_THREADS
}

vector<int> Analyzer::find_nbrs(vector<double> x, int k) 
// returns k nearest neighbors 
{
  // Py_BEGIN_ALLOW_THREADS
  tree->annkSearch(&x[0], k, idx, dist, 0);
  vector<int> v(idx, idx+k);
  return v;
  // Py_END_ALLOW_THREADS
}

double Analyzer::get_h()
  // getter for bandwidth h
{
  return h;
}

void Analyzer::set_h(double _h)
  // setter for bandwidth h
{
  h = _h;
}

double Analyzer::calc_h()
  // automatically calculate optimal value for h as median separation of seed points
{
  // Py_BEGIN_ALLOW_THREADS
  int num_seeds = (int) sqrt(float(n));
  if (num_seeds > k) {
    num_seeds = k;
  }
  vector<int> pt_idx(n);
  for (int i=0; i<n; ++i) {
    pt_idx[i] = i;
  }
  random_shuffle(pt_idx.begin(), pt_idx.end());
  vector<double> h_vec;
  for (int i=0; i<num_seeds; ++i) {
    tree->annkSearch(data[pt_idx[i]], num_seeds, idx, dist, 0);
    h_vec.push_back(dist[num_seeds-1]);
  }
  return sqrt(h_vec[num_seeds/2]);
  // Py_END_ALLOW_THREADS
}

// Uniform_Analyzer

Uniform_Analyzer::Uniform_Analyzer(vector<vector<double> > _data, int _dim, int _n, int _k, double _h, double _alpha):
  // constructor for Unifrom_Analyzer
  Analyzer(_data, _dim, _n, _k, _h, _alpha) {}

vector<double> Uniform_Analyzer::mean_shift(vector<double> x)
  // mean shift with uniform kernel (gradient ascent on epanechnikov)
{
  // Py_BEGIN_ALLOW_THREADS
  int num = min(k, tree->annkFRSearch(&x[0], h*h, k, idx, dist, alpha));
  vector<double> sum(dim, 0.0);
  for (int i=0; i<num; ++i)
    for (int d=0; d<dim; ++d)
      sum[d] += data[idx[i]][d];
  for (int d=0; d<dim; d++)
    sum[d] /= num;
  for (int d=0; d<dim; d++)
    sum[d] -= x[d];
  return sum;
  // Py_END_ALLOW_THREADS
}

double Uniform_Analyzer::density(vector<double> x)
  // return sample density with uniform kernel
{
  return tree->annkFRSearch(&x[0], h*h, k, idx, dist, 0);
}  



// Epanechnikov_Analyzer

Epanechnikov_Analyzer::Epanechnikov_Analyzer(vector<vector<double> > _data, int _dim, int _n, int _k, double _h, double _alpha):
  // constructor for Epanechnikov_Analyzer
  Analyzer(_data, _dim, _n, _k, _h, _alpha) {}

vector<double> Epanechnikov_Analyzer::mean_shift(vector<double> x)
  // mean shift with epanechnikov kernel (gradient ascent on biweight)
{
  // Py_BEGIN_ALLOW_THREADS
  int num = min(k, tree->annkFRSearch(&x[0], h*h, k, idx, dist, alpha));
  vector<double> sum(dim, 0.0);
  double denom(0.0);
  for (int i=0; i<num; ++i) {
    denom += h*h - dist[i];
    for (int d=0; d<dim; d++)
      sum[d] += (h*h - dist[i])*data[idx[i]][d];
  }
  for (int d=0; d<dim; d++)
    sum[d] /= denom;
  for (int d=0; d<dim; d++)
    sum[d] -= x[d];
  return sum;
  // Py_END_ALLOW_THREADS
}
  
double Epanechnikov_Analyzer::density(vector<double> x)
  // return sample density with epanechnikov kernel
{
  int num = min(k, tree->annkFRSearch(&x[0], h*h, k, idx, dist, alpha));
  double sum(0.0);
  for (int i=0; i<num; ++i) {
    sum += (h*h - dist[i]);
  }
  return sum/(h*h);
}  

