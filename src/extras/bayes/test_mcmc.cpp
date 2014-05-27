#include "common.hpp"
#include "distributions.hpp"
#include "utils.hpp"
#include "mcmc.hpp"
#include "fixtures.hpp"
#include <boost/test/unit_test.hpp>

using boost::unit_test::test_suite;

// use column order matrices for lapack routines

typedef ublas::matrix<double, ublas::column_major> matrix_t;

mcmc_fixture f;

void test_mcmc() {
  int nit = 0;
  int nmc = 100;

  mcmc(nit, nmc, f.x, f.n, f.p, f.k, f.pi, f.mu, f.Omega, f.z);

  ublas::vector<ublas::matrix<double> > Sigma_ans;
  Sigma_ans.resize(f.k);
  Sigma_ans(0).resize(f.p, f.p);
  Sigma_ans(0)(0,0) = 5; Sigma_ans(0)(0,1) = 0;   
  Sigma_ans(0)(1,0) = 0; Sigma_ans(0)(1,1) = 5; 
  Sigma_ans(1).resize(f.p, f.p);
  Sigma_ans(1)(0,0) = 5; Sigma_ans(1)(0,1) = 0;   
  Sigma_ans(1)(1,0) = 0; Sigma_ans(1)(1,1) = 5; 
  Sigma_ans(2).resize(f.p, f.p);
  Sigma_ans(2)(0,0) = 5; Sigma_ans(2)(0,1) = 0;   
  Sigma_ans(2)(1,0) = 0; Sigma_ans(2)(1,1) = 5; 

  ublas::vector<ublas::vector<double> > mu_ans;
  mu_ans.resize(f.k);
  mu_ans(0).resize(f.p);
  mu_ans(0)(0) = 25; mu_ans(0)(1) = 25; 
  mu_ans(1).resize(f.p);
  mu_ans(1)(0) = 9; mu_ans(1)(1) = 9; 
  mu_ans(2).resize(f.p);
  mu_ans(2)(0) = 19; mu_ans(2)(1) = 19;

  ublas::vector<double> pi_ans(f.k);
  pi_ans(0) = 500.0/750; pi_ans(1) = 150.0/750; pi_ans(2) = 100.0/750;

  // calc covariance matrix as inverse of precision matrix
  ublas::vector<ublas::matrix<double> > Sigma(f.Omega);
  for (size_t i=0; i<f.Omega.size(); ++i)
    ublas::InvertMatrix(f.Omega(i), Sigma(i));

  cout << "MCMC iters: " << nmc << "\n";
  cout << "pi          " << f.pi << "\n";
  cout << "mu          " << f.mu << "\n";
  cout << "Omega       " << f.Omega << "\n";
  cout << "Sigma       " << Sigma << "\n\n";

  for (int i=0; i<f.k; ++i) {
    BOOST_CHECK(norm_inf(f.mu(i) - mu_ans(i)) < 1.5);
    BOOST_CHECK(norm_inf(Sigma(i) - Sigma_ans(i)) < 5);
  }
  BOOST_CHECK(norm_inf(f.pi - pi_ans) < 0.1);
}

test_suite*
init_unit_test_suite(int, char* []) {
  test_suite* test = BOOST_TEST_SUITE("test_mcmc");
  test->add(BOOST_TEST_CASE(&test_mcmc), 0);
  
  return test;
}
