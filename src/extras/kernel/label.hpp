#ifndef LABEL_HPP
#define LABEL_HPP

#include "common.hpp"
#include "analyzer.hpp"

typedef boost::shared_ptr<Analyzer> Analyzer_ptr;

Analyzer_ptr create_analyzer(string name, vector<vector<double> > _data, int _dim, int _n, int _k, double _h, double _alpha);
int find_majority(vector<int> v);
map<int, int> label_seeds(map<vector<double>, vector<int> > modes);
map<int, int> label_points(string name, vector<vector<double> > data, map<vector<double>, vector<int> > modes, int nbrs);

#endif
