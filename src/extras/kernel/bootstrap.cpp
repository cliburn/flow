#include "common.hpp"
#include "analyzer.hpp"
#include "label.hpp"

typedef boost::shared_ptr<Analyzer> Analyzer_ptr;

int main() {
  // ANNpointArray data;
  int n = 10000;
  int k = n;
  int dim = 3;
  int seed = 123457;
  double h = 0.0;
  double alpha = 0.0;
  string analyzer_name = "Epanechnikov";

  // make up control data
  imsls_random_seed_set(seed);
  vector<vector<double> > c_data;
  vector<double> v;
  for (int i=0; i<n; ++i) {
    v.clear();
    for (int j=0; j<dim; ++j) {
      v.push_back(5.0+1.0*imsls_d_random_normal(1, 0)[0]);
    }
    c_data.push_back(v);
  }

  /*
  // export control data
  for (int i=0; i<c_data.size(); ++i) {
    cout << c_data[i][0];
    for (int j=1; j<c_data[i].size(); ++j) {
      cout << "," << c_data[i][j];
    }
    cout << endl;
  }
  */

  // make up test data
  imsls_random_seed_set(seed);
  vector<vector<double> > t_data;
  for (int i=0; i<n; ++i) {
    v.clear();
    for (int j=0; j<dim-1; ++j) {
      v.push_back(5.0+1.0*imsls_d_random_normal(1, 0)[0]);
    }
    v.push_back(6.0+1.0*imsls_d_random_normal(1, 0)[0]);
    t_data.push_back(v);
  }

  /*
  // export test data
  cout << endl;
  cout << endl;
  for (int i=0; i<t_data.size(); ++i) {
    cout << t_data[i][0];
    for (int j=1; j<t_data[i].size(); ++j) {
      cout << "," << t_data[i][j];
    }
    cout << endl;
  }
  */

  // create test analyzer with same h
  Analyzer_ptr t_ap = create_analyzer(analyzer_name, t_data, dim, n, k, h, alpha);
  h = t_ap->calc_h();
  cout << h << endl;

  // find seeds for test data
  double min_sep = h;
  vector<int> seeds = t_ap->find_seeds(min_sep, 0, 0);

  /*
  // export seeds
  cout << endl;
  cout << endl;
  for (int i=0; i<seeds.size(); ++i) {
    cout << seeds[i] << endl;
  }
  */
  cout << endl << endl;
  */

  vector<vector<double> > bootstrap_densities(seeds.size());
  int nsamp=0;
  for (int kk=0; kk<nsamp; ++kk) {
    cerr << kk << endl;
    // bootstrap on control set
    vector<vector<double> > bootstrap_sample;
    // create bootstrap sample and analzer
    int* ir = imsls_d_random_uniform_discrete(c_data.size(), c_data.size(), 0);
    for (int i=0; i<c_data.size(); ++i) {
      vector<double> v = c_data[ir[i]-1];
      for (int j=0; j<v.size(); ++j) {
	v[j] += 0.001+1.0*imsls_d_random_normal(1, 0)[0];
      }
      bootstrap_sample.push_back(v);
    }
    Analyzer_ptr c_ap = create_analyzer(analyzer_name, bootstrap_sample, dim, n, k, h, alpha);
    // get density at every seed location
    for (int j=0; j<seeds.size(); ++j) {
      bootstrap_densities[j].push_back(c_ap->density(t_data[seeds[j]]));
    }
  }

  for (int i=0; i<bootstrap_densities.size(); ++i) {
    cout << bootstrap_densities[i][0];
    for (int j=1; j<bootstrap_densities[i].size(); ++j) {
      cout << "," << bootstrap_densities[i][j];
    }
    cout << endl;
  }
}

