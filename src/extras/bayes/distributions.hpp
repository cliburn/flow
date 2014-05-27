#ifndef DISTRIBUTIONS_HPP
#define DISTRIBUTIONS_HPP

#include "common.hpp"
#include <boost/numeric/bindings/lapack/gesvd.hpp>

typedef ublas::matrix<double, ublas::column_major> matrix_t;

ublas::vector<double> dirichlet_rnd(const ublas::vector<int>& nz);
ublas::matrix<double> wishart_rnd(const int df, ublas::matrix<double>& S);

ublas::matrix<double> wishart_InvA_rnd(const int df, ublas::matrix<double>& S);
ublas::vector<ublas::matrix<double> > wishart_rnd(const int df, ublas::matrix<double>& S, const int mc);
ublas::vector<ublas::matrix<double> > wishart_InvA_rnd(const int df, ublas::matrix<double>& S, const int mc);
ublas::vector<double> mvnormpdf(const ublas::matrix<double>& x, const ublas::vector<double>& mu, const ublas::matrix<double>& S);
double det(const ublas::matrix<double>& A);

#endif
