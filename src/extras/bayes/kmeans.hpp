#ifndef KMEANS_HPP
#define KMEANS_HPP

#include "common.hpp"
#include <algorithm>
#include <limits>

namespace ublas = boost::numeric::ublas;

// ublas::vector<int> calc_z(const ublas::matrix<double>& data, const ublas::vector<ublas::vector<double> >& centroids, const int n, const int k, const int p);
// ublas::vector<ublas::vector<double> > calc_centroids(const ublas::matrix<double>& data, const ublas::vector<int>& z, const int n, const int k, const int p);
ublas::vector<ublas::vector<double> > kmeans(const ublas::matrix<double>& data, const int n, const int k, const int p, const double tol);

#endif
