#ifndef MATH_UTILS_HPP
#define MATH_UTILS_HPP

#include <boost/numeric/bindings/lapack/gesvd.hpp>

namespace ublas = boost::numeric::ublas;
namespace lapack = boost::numeric::bindings::lapack;
// namespace atlas = boost::numeric::bindings::atlas;

typedef ublas::matrix<double, ublas::column_major> matrix_t;

void set_rseed(const unsigned int& seed1,
               const unsigned int& seed2);

void set_state(const unsigned int& seed1 = time(NULL),
               const unsigned int& seed2 = clock());

namespace Rmath {
  //! convenience functions to get vector of results
  ublas::vector<double> runif(double a, double b, int n);
  ublas::vector<double> rnorm(double mu, double sigma, int n);
  ublas::vector<double> rgamma(double alpha, double beta, int n);
}

ublas::vector<int> rdisc(const unsigned n, const ublas::vector<double>& p);
int rdisc(const ublas::vector<double>& p);
ublas::matrix<double> rprod(const ublas::matrix<double>& M, const ublas::vector<double>& V);
void svd0(ublas::matrix<double, ublas::column_major>& x, ublas::matrix<double, ublas::column_major>& P, ublas::vector<double>& D, ublas::matrix<double, ublas::column_major>& F);
#endif

