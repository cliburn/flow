#include "common.hpp"
#include "math_utils.hpp"

int is_initialized = 0;

// Set seed in C++ code using seed values.
void set_rseed(const unsigned int& seed1, const unsigned int& seed2)
{
  Rmath::set_seed(seed1, seed2);
}

// Set seed in C++ code using seed values.
void set_state(const unsigned int& seed1, const unsigned int& seed2)
{
  if(is_initialized)
    ;
  else
    {
      Rmath::set_seed(seed1, seed2);
      is_initialized = 1;
    }
}

namespace Rmath {
  ublas::vector<double> runif(double a, double b, int n) {
    ublas::vector<double> result(n);
    for (int i=0; i<n; ++i)
      result(i) = runif(a, b);
    return result;
  }
  
  ublas::vector<double> rnorm(double mu, double sigma, int n) {
    ublas::vector<double> result(n);
    for (int i=0; i<n; ++i)
      result(i) = rnorm(mu, sigma);
    return result;
  }

  ublas::vector<double> rgamma(double alpha, double beta, int n) {
    ublas::vector<double> result(n);
    for (int i=0; i<n; ++i)
      result(i) = rgamma(alpha, beta);
    return result;
  }
}

int rdisc(const ublas::vector<double>& p) {
  int idx = -1;
  // construct cumulative probability
  ublas::vector<double> q(p.size());
  std::partial_sum(p.begin(), p.end(), q.begin()); 

  double r = Rmath::runif(0, 1);
  for (size_t j=0; j<q.size(); ++j)
    if (r < q[j]) {
      idx = j;
      break;
    }
  return idx;  
}

ublas::vector<int> rdisc(const unsigned n, const ublas::vector<double>& p) {
  ublas::vector<int> idx(n);
  // construct cumulative probability
  ublas::vector<double> q(p.size());
  std::partial_sum(p.begin(), p.end(), q.begin());

  for (size_t i=0; i<n; ++i) {
    double r = Rmath::runif(0, 1);
    for (size_t j=0; j<p.size(); ++j) {
      if (r < q[j]) {
	idx(i) = j;
	break;
      }
    }
  }
  
  return idx;  
}  

ublas::matrix<double> rprod(const ublas::matrix<double>& M, const ublas::vector<double>& V) {
  return element_prod(M, outer_prod(ublas::scalar_vector<double>(V.size(), 1), V));
}

void svd0(ublas::matrix<double, ublas::column_major>& S, ublas::matrix<double, ublas::column_major>& P, ublas::vector<double>& D, ublas::matrix<double, ublas::column_major>& F) {
  int p = S.size1();
  int n = S.size2();
  lapack::gesvd('A', 'A', S, D, P, F);
  if (p<n)
    D = project(D, range(0, p));
}
    
