#ifndef FIXTURES_HPP
#define FIXTURES_HPP

#include "common.hpp"
#include "kmeans.hpp"
typedef ublas::matrix<double, ublas::column_major> matrix_t;

struct mcmc_fixture_base
{
  int n; // number of data points
  int k; // number of components
  int p; // number of dimensions
  ublas::matrix<double> x;
  ublas::vector<double> pi;
  ublas::vector<ublas::vector<double> > mu;
  ublas::vector<ublas::matrix<double> > Omega;
  ublas::vector<int> z;

  mcmc_fixture_base(int _n, int _k, int _p, string data_file, string init_file): n(_n), k(_k), p(_p) {
    x = read_data(data_file.c_str(), n, p);

//     // scale data to [0, 1]
//     double max_value = 0;
//     double tmp;
//     for (int i=0; i<p; ++i) {
//       tmp = norm_inf(row(x, i));
//       if (tmp > max_value)
//     	max_value = tmp;
//     }
    
//     x /= max_value;

    pi.resize(k);
    // assign equal weight
    for (int i=0; i<k; ++i)
      pi(i) = 1.0/k;

    // assign omega to be identity matrix * some scaling factor
    Omega.resize(k);
    for (int i=0; i<k; ++i) {
      Omega(i).resize(p, p);
      Omega(i) = ublas::identity_matrix<double>(p, p);
    }

    // assign mu with kmeans
    mu = kmeans(x, n, k, p, 1e-6);

    //     // assign random means
    //     mu.resize(k);
    //     for (int i=0; i<k; ++i) {
    //       mu(i).resize(p);
    //       for (int j=0; j<p; ++j) {
    // 	// 	mu(i)(j) = std::rand() % int(max_value);
    //  	mu(i)(j) = Rmath::runif(0, 1);
    //       }
    //     }
    
    // have routine to read in initial values for mu
    if (init_file != "")
      mu = read_mu(init_file.c_str(), k, p);

    z.resize(n);
    for (size_t i=0; i<z.size(); ++i)
      z(i) = std::rand() % k;
  }
};


struct mcmc_fixture_1d
{
  int n; // number of data points
  int k; // number of components
  int p; // number of dimensions
  ublas::matrix<double> x;
  ublas::vector<double> pi;
  ublas::vector<ublas::vector<double> > mu;
  ublas::vector<ublas::matrix<double> > Omega;
  ublas::vector<int> z;

  mcmc_fixture_1d(): n(75000), k(3), p(1) {
    x = read_data("../data/mcmc_1d_data.txt", n, p);
    
    pi.resize(k);
    // assign equal weight
    for (size_t i=0; i<pi.size(); ++i)
      pi(i) = 1.0/k;
    // assign means as k x p vector of vectors
    Omega.resize(k);
    Omega(0).resize(p, p);
    Omega(0)(0,0) = 1;
    Omega(1).resize(p, p);
    Omega(1)(0,0) = 1;
    Omega(2).resize(p, p);
    Omega(2)(0,0) = 1;

    mu.resize(k);
    mu(0).resize(p);
    mu(0)(0) = 5; 
    mu(1).resize(p);
    mu(1)(0) = 15; 
    mu(2).resize(p);
    mu(2)(0) = 25;
    
    z.resize(n);
    for (size_t i=0; i<z.size(); ++i)
      z(i) = std::rand() % k;
  }
};

struct mcmc_fixture
{
  int n; // number of data points
  int k; // number of components
  int p; // number of dimensions
  ublas::matrix<double> x;
  ublas::vector<double> pi;
  ublas::vector<ublas::vector<double> > mu;
  ublas::vector<ublas::matrix<double> > Omega;
  ublas::vector<int> z;

  mcmc_fixture(): n(750), k(3), p(2) {
    x = read_data("../data/mcmc_data.txt", n, p);
    
    double max_value = 0;
    double tmp;
    for (int i=0; i<p; ++i) {
      tmp = norm_inf(row(x, i));
      if (tmp > max_value)
	max_value = tmp;
    }

    pi.resize(k);
    // assign equal weight
    for (int i=0; i<k; ++i)
      pi(i) = 1.0/k;
    // assign means as k x p vector of vectors
    Omega.resize(k);
    for (int i=0; i<k; ++i) {
      Omega(i).resize(p, p);
      Omega(i) = ublas::identity_matrix<double>(p, p);
    }

    mu.resize(k);
    for (int i=0; i<k; ++i) {
      mu(i).resize(p);
      for (int j=0; j<p; ++j) {
	mu(i)(j) = std::rand() % int(max_value);
      }
    }
    
    z.resize(n);
    for (size_t i=0; i<z.size(); ++i)
      z(i) = std::rand() % k;
  }
};

#endif
