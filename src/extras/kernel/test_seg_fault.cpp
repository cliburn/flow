#include "common.hpp"
#include "analyzer.hpp"
#include "label.hpp"

typedef boost::shared_ptr<Analyzer> Analyzer_ptr;

int main(int argc, char* argv[]) {
  // ANNpointArray data;
  // int n = 94569;
  cout << "Begin program" << endl;

  int n = atoi(argv[1]);
  if (n > 94569) {
    n = 94659;
  }
  int k = n;
  int dim = 4;
  // int seed = 123457;
  double h = 0.0; 
  double alpha = 0.0;
  string analyzer_name = "Uniform";

  vector<vector<double> > pts;
  vector<double> pt;
  
  string s;
  double p;
  ifstream infile("../data/3FITC-4PE.004.txt");
  
  // skip header

  for (int j=0; j<dim; ++j) {
    infile >> s;
  }

  // read in data
  for (int i=0; i<n; ++i) {
    pt.clear();
    for (int j=0; j<dim; ++j) {
      infile >> p;
      pt.push_back(p);
    }
    pts.push_back(pt);
  }

  /*
    for (int i=0; i<n; ++i) {
    cout << "[" << data[i][0];
    for (int j=1; j<dim; ++j) {
      cout << "\t" << data[i][j];
    }
    cout << "]" << endl;
  }
  */

  // make up some random data with 5 modes
  /*
  imsls_random_seed_set(seed);
  vector<vector<double> > data;
  vector<double> v(dim, 0.0);
  for (int i=0; i<n; ++i) {
    v.clear();
    double r = imsls_d_random_uniform(1, 0)[0];
    if (r < 0.2) {
      for (int j=0; j<dim; ++j) {
	v.push_back(5.0+1.0*imsls_d_random_normal(1, 0)[0]);
      }
    }	
    else if (r < 0.4) {
      for (int j=0; j<dim; ++j) {
	v.push_back(7.0+1.0*imsls_d_random_normal(1, 0)[0]);
      }
    }
    else if (r < 0.7) {
      for (int j=0; j<dim; ++j) {
	v.push_back(9.0+1.0*imsls_d_random_normal(1, 0)[0]);
      }
    }
    else if (r < 0.9) {
      for (int j=0; j<dim; ++j) {
	v.push_back(11.0+1.0*imsls_d_random_normal(1, 0)[0]);
      }
    }
    else {
      for (int j=0; j<dim; ++j) {
	v.push_back(13.0+1.0*imsls_d_random_normal(1, 0)[0]);
      }
    }
    data.push_back(v);
  }
  */
  //   for (int i=0; i<data.size(); ++i) {
  //     cout << data[i][0];
  //     for (int j=1; j<data[i].size(); ++j) {
  //       cout << "," << data[i][j];
  //     }
  //     cout << endl;
  //   }

  // Analyzer_ptr ap(new Epanechnikov_Analyzer(data, dim, n, k, h, alpha));
  cout << "Begin create analyzer" << endl;
  Analyzer_ptr ap = create_analyzer(analyzer_name, pts, dim, n, k, h, alpha);
  cout << "End create analyzer" << endl;

  /*
  vector<double> x(dim, 0.0);
  vector<double> v(dim, 0.0);
  for (int i=0; i<dim; ++i)
    x[i] = data[0][i];

  // test get_h
  cout << ">> test calc_h" << endl;
  double h_opt = ap->get_h();
  cout << "h_opt = " << h_opt << endl;

  // test mean shift with kernel
  cout << ">> test mean shift with kernel" << endl;
  vector<double> shift = ap->mean_shift(x);
  for (int i=0; i<shift.size(); ++i) 
    cout << shift[i] << '\t';
  cout << endl;

  // test find_seeds
  cout << ">> test find_seeds" << endl;
  double min_sep = ap->calc_h();
  vector<int> seeds = ap->find_seeds(min_sep, 0, 0);
  cout << "Num seeds: " << seeds.size() << endl;

  // test density
  cout << ">> test density" << endl;
  double dens1 = ap->density(x);
  cout << dens1 << endl;

  // test dip_test
  cout << ">> test dip_test" << endl;
  vector<double> x1(dim, 0.0);
  for (int i=0; i<dim; ++i)
    x1[i] = data[1][i];
  bool b1 = ap->dip_test(x, x1, 1.0);
  cout << b1 << endl;

  // test norm
  cout << ">> test norm" << endl;
  v[0] = 1.0; v[1] = 1.0;
  cout << ap->norm(v) << endl;

  // test euclid_dist
  cout << ">> test euclid_dist" << endl;
  vector<double> v1(2, 1.0);
  vector<double> v2(2, 2.0);
  cout << ap->euclid_dist(v1, v2) << endl;
  

  // test find_modes
  cout << ">> test find_modes" << endl;
  map<int, vector<double> > modes = ap->find_modes(seeds, 1e-2);
  map<int, vector<double> >::iterator map_it;
  cout << modes.size() << endl;

  // test merge_modes 
  cout << ">> test merge_modes" << endl;
  map<vector<double>, vector<int> > mmodes = ap->merge_modes(modes, 0.1);
  map<vector<double>, vector<int> >::iterator mmap_it;
  for (mmap_it = mmodes.begin(); mmap_it != mmodes.end(); ++ mmap_it) {
    vector<double> v = mmap_it->first;
    cout << "[" << v[0];
    for (int i=1; i<v.size(); ++i) {
      cout << ", " << v[i];
    }
    cout << "]: "; 
    cout << (mmap_it->second).size() << endl;
  }

  // test pop_check_modes
  cout  << ">> test pop_check_modes" << endl;
  int min_pop = 2;
  mmodes = ap->pop_check_modes(mmodes, min_pop);
  for (mmap_it = mmodes.begin(); mmap_it != mmodes.end(); ++ mmap_it) {
    vector<double> v = mmap_it->first;
    cout << "[" << v[0];
    for (int i=1; i<v.size(); ++i) {
      cout << ", " << v[i];
    }
    cout << "]: ";
    cout << (mmap_it->second).size() << endl;
  }

  // test check_modes
  double dip_ratio = 0.95;
  cout << ">> test check_modes" << endl;
  mmodes = ap->check_modes(mmodes, dip_ratio);
  for (mmap_it = mmodes.begin(); mmap_it != mmodes.end(); ++ mmap_it) {
    vector<double> v = mmap_it->first;
    cout << "[" << v[0];
    for (int i=1; i<v.size(); ++i) {
      cout << ", " << v[i];
    }
    cout << "]: "; 
    cout << (mmap_it->second).size() << endl;
  }

  // test label seeds
  cout << ">> test label seeds" << endl;
  map<int, int> s_labels = label_seeds(mmodes);
  for (map<int, int>::iterator it=s_labels.begin(); it!=s_labels.end(); ++it) {
    cout << it->first << ": " << it->second << "\t";
  }
  cout << endl;

  // test find majority
  cout << ">> test find majority" << endl;
  vector<int> z;
  z.push_back(1);
  z.push_back(0);
  z.push_back(1);
  z.push_back(2);
  z.push_back(2);
  z.push_back(1);
  cout << find_majority(z) << endl;

  // test label points
  int nbrs = 1+floor(mmodes.size()/5.0);
  // int nbrs = 1;
  cout << "nbrs = " << nbrs << endl;
  cout << ">> test label points" << endl;
  map<int, int> p_labels = label_points(analyzer_name, data, mmodes, nbrs);
  map<int, int> clusters;
  for (map<int, int>::iterator it=p_labels.begin(); it!=p_labels.end(); ++it) {
    clusters[it->second] = 0;
  }
  for (map<int, int>::iterator it=p_labels.begin(); it!=p_labels.end(); ++it) {
    ++clusters[it->second];
  }
  for (map<int, int>::iterator it=clusters.begin(); it!=clusters.end(); ++it) {
    cout << it->first << ": " << it->second << endl;
  }
  cout << endl;
  */
  cout << "Test OK - exiting" << endl;
  return 0;
}
