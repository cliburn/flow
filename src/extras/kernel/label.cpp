#include "common.hpp"
#include "analyzer.hpp"

typedef boost::shared_ptr<Analyzer> Analyzer_ptr;

Analyzer_ptr create_analyzer(string name, vector<vector<double> > _data, int _dim, int _n, int _k, double _h, double _alpha)
  // factory method for Analyzers
{
  if (name == "Epanechnikov") {
    Analyzer_ptr ap(new Epanechnikov_Analyzer(_data, _dim, _n, _k, _h, _alpha));
    return ap;
  } else {
    Analyzer_ptr ap(new Uniform_Analyzer(_data, _dim, _n, _k, _h, _alpha));
    return ap;
  }
}

int find_majority(vector<int> v)
  // linear time majority vote algorithm by Boyer
  // http://www.cs.utexas.edu/users/moore/best-ideas/mjrty/index.html
{
  int cnt = 1;
  int max_elem = v[0];
  for (unsigned i=1; i<v.size(); ++i) {
    if (cnt==0) {
      max_elem = v[i];
      ++cnt;
    }
    if (max_elem == v[i]) {
      ++cnt;
    }
    else {
      --cnt;
    }
  }
  return max_elem;
}

map<int, int> label_seeds(map<vector<double>, vector<int> > modes) 
  // label each seed with the cluster number
{
  map<vector<double>, vector<int> >::iterator mode_it;
  map<int, int> seed_labels;
  int label = 0;
  for (mode_it=modes.begin(); mode_it!=modes.end(); ++mode_it) {
    vector<int> m = mode_it->second;
    for (unsigned i=0; i<m.size(); ++i) {
      seed_labels[m[i]] = label;
    }
    ++label;
  }
  return seed_labels;
}

map<int, int> label_points(string analyzer_name, vector<vector<double> > data, map<vector<double>, vector<int> > modes, int nbrs)
  // label each data point with the cluster number
{
  map<int, int> seed_labels = label_seeds(modes);
  map<int, int> point_labels;
  map<vector<double>, vector<int> >::iterator seed_it;
  map<int, int> seed_mapper;
  vector<vector<double> > seed_data;
  int j = 0; // labels ALL seeds
  for (seed_it=modes.begin(); seed_it!=modes.end(); ++seed_it) {
    vector<int> seed_idx = seed_it->second;
    for (unsigned i=0; i<seed_idx.size(); ++i, ++j) {
      seed_data.push_back(data[seed_idx[i]]);
      seed_mapper[j] = seed_idx[i];
    }
  }
  int dim = seed_data[0].size();
  double alpha = 0;
  double h = 0;
  // Analyzer_ptr ap(new Epanechnikov_Analyzer(seed_data, dim, seed_data.size(), nbrs, h, alpha));
  Analyzer_ptr ap = create_analyzer(analyzer_name, seed_data, dim, seed_data.size(), nbrs, h, alpha);

  // label by majority vote
  for (unsigned i=0; i<data.size(); ++i) {
    vector<int> knn = ap->find_nbrs(data[i], nbrs);
    vector<int> knn_labels;
    for (unsigned j=0; j<knn.size(); ++j) {
      knn_labels.push_back(seed_labels[seed_mapper[knn[j]]]);
    }
    int maj = find_majority(knn_labels);
    point_labels[i] = maj;
  }

  // put original labels back on seeds
  for (map<int, int>::iterator it=seed_labels.begin(); it!=seed_labels.end(); ++it) {
    point_labels[it->first] = it->second;
  }

  return point_labels;
}

