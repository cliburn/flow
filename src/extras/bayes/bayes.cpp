#include "bayes.hpp"
#include "Python.h"

void Bayes::init(const ublas::matrix<double>& _x, const int _n, const int _p, const int _k) {
  Py_BEGIN_ALLOW_THREADS

  // data
  x = _x;
  n = _n;
  p = _p;
  k = _k;

  current = 0.0;
  loglik = -1e100;
  ml_pi = ublas::zero_vector<double>(k);
  ml_mu.resize(k);
  for (int i=0; i<k; ++i)
    ml_mu(i) = ublas::zero_vector<double>(p);
  ml_Omega.resize(k);
  for (int i=0; i<k; ++i) {
    ml_Omega(i).resize(p, p);
    ml_Omega(i) = ublas::zero_matrix<double>(p, p);
  }

  probx.resize(k, n);
  for (int i=0; i<k; ++i)
    for (int j=0; j<n; ++j)
      probx(i, j) = 0.0;

  // INITIALISE EXTERNALLY
  pi.resize(k);
  // assign equal weight
  for (int i=0; i<k; ++i)
    pi(i) = 1.0/k;

  // assign omega to be identity matrix * some scaling factor
  Omega.resize(k);
  ml_Omega.resize(k);
  for (int i=0; i<k; ++i) {
    Omega(i).resize(p, p);
    Omega(i) = 0.01*ublas::identity_matrix<double>(p, p);
  }

  // assign mu with kmeans
  mu = kmeans(x, n, k, p, 1e-6);
  
  // assign random indices to z
  z.resize(n);
  for (size_t i=0; i<z.size(); ++i)
    z(i) = std::rand() % k;
    
  Py_END_ALLOW_THREADS
}
  

void Bayes::sample_zpi() {
  //! sample classification
  // ublas::matrix<double> probx(k, n);

  for (int i=0; i<k; ++i) {
    row(probx, i).assign(pi(i) * mvnormpdf(x, mu(i), Omega(i)));
  }

  // print out likelihood
  for (int i=0; i<n; ++i) {
    double tmpsum = sum(column(probx, i));
    if (tmpsum > 0) {
      current += log(tmpsum);
    }
  }
  if (loglik < current && current < 0) {
    loglik = current;
    ml_pi.assign(pi);
    ml_mu.assign(mu);
    ml_Omega.assign(Omega);
  }
  current = 0.0;
  
  ublas::vector<int> nz(k);
  for (int i=0; i<k; ++i)
    nz(i) = 0;

  for (int i=0; i<n; ++i) {
    column(probx, i) /= sum(column(probx, i));
    z(i) = rdisc(column(probx, i));
  }

  // calculate counts and complete data log likelihood
  for (int i=0; i<k; ++i)
    for (int j=0; j<n; ++j)
      if (z[j] == i) {
	nz(i) += 1;
      }

  pi = dirichlet_rnd(nz);

  // get indices sorted in reverse order
  std::vector<int> idx(argsort(pi));
  std::reverse(idx.begin(), idx.end());
  ublas::indirect_array<> u_idx(idx.size());
  for (size_t i=0; i<idx.size(); ++i)
    u_idx(i) = idx[i];

  pi = project(pi, u_idx);
  mu = project(mu, u_idx);
  Omega = project(Omega, u_idx);

  ublas::vector<int> oldz(z);
  for (int i=0; i<k; ++i)
    for (size_t j=0; j<oldz.size(); ++j)
      if (i == oldz[j])
	z[j] = idx[i];

}

void Bayes::sample_muOmega() {
  double tau = 10.0;
  int d0 = p + 2;
  // matrix_t S0(p, p);
  ublas::matrix<double> S0(p, p);
  S0 = d0 * ublas::identity_matrix<double>(p, p)/4.0;
  
  std::vector<int> idx;
  ublas::indirect_array<> irow(p);
  // projection - want every row
  for (size_t i=0; i<irow.size(); ++i)
    irow(i) = i;
  
  // size_t rank;
  ublas::matrix<double> S(p, p);
  // matrix_t SS(p, p);
  ublas::matrix<double> SS(p, p);
  ublas::matrix<double> Omega_inv(p, p);

  // identity matrix for inverting cholesky factorization
  ublas::matrix<double> I(p, p);
  I.assign(ublas::identity_matrix<double> (p, p));
  ublas::symmetric_adaptor<ublas::matrix<double>, ublas::upper> SH(I);

  // triangular matrix for cholesky_decompose
  ublas::triangular_matrix<double, ublas::lower, ublas::row_major> L(p, p);

  int df;
  for (int j=0; j<k; ++j) {
    idx = find_all(z, j);
    int n_idx = idx.size();

    ublas::matrix<double> xx(p, n_idx);
    ublas::matrix<double> e(p, n_idx);
    // ublas::matrix<double> m(p, 1);
    ublas::vector<double> m(p);

    ublas::indirect_array<> icol(n_idx);
    for (size_t i=0; i<idx.size(); ++i)
      icol(i) = idx[i];
    if (n_idx > 0) {
      double a = tau/(1.0 + n_idx*tau);
      //! REFACTOR - should be able to do matrix_sum directly on projection rather than make a copy?
      xx.assign(project(x, irow, icol));
      m.assign(ublas::matrix_sum(xx, 1)/n_idx);
      // e.assign(xx - outer_prod(column(m, 0), ublas::scalar_vector<double>(n_idx, 1)));
      e.assign(xx - outer_prod(m, ublas::scalar_vector<double>(n_idx, 1)));
      S.assign(prod(e, trans(e)) + outer_prod(m, m) * n_idx * a/tau);
      // SS = trans(S) + S0;
      SS = S + S0;
      df = d0 + n_idx;

      // Omega(j).assign(wishart_rnd(df, SS));
      Omega(j).assign(wishart_InvA_rnd(df, SS));
      SH.assign(Omega(j));
      cholesky_decompose(SH, L);
      Omega_inv.assign(solve(SH, I, ublas::upper_tag()));
      mu(j).assign(a*n_idx*m + sqrt(a)*prod(Omega_inv, Rmath::rnorm(0, 1, p)));
    } else {
      // Omega(j).assign(wishart_rnd(d0, S0));
      Omega(j).assign(wishart_InvA_rnd(d0, S0));
      SH.assign(Omega(j));
      cholesky_decompose(SH, L);
      Omega_inv.assign(solve(SH, I, ublas::upper_tag()));
      mu(j).assign(sqrt(tau) * prod(Omega_inv, Rmath::rnorm(0, 1, p)));
    }
  }
}

void Bayes::mcmc(const int nit, const int nmc, const string& data_file, const bool record) {

  Py_BEGIN_ALLOW_THREADS

  // assign storage;
  save_z.resize(nmc);
  save_pi.resize(nmc);
  save_mu.resize(nmc);
  save_Omega.resize(nmc);
  for (int i=0; i<nmc; ++i) {
    save_z[i].resize(n);
    save_pi[i].resize(k);
    save_mu[i].resize(k);
    save_Omega[i].resize(k);
    for (int j=0; j<k; ++j) {
      save_mu[i][j].resize(p);
      save_Omega[i][j].resize(p, p);
    }
  }

  //! MCMC routine
  for (int i=0; i<(nit + nmc); ++i) {
    sample_zpi();

    // save MCMC samples
    if (i >= nit) {
      	save_z.push_back(z);
      	save_pi.push_back(pi);
      	save_mu.push_back(mu);
      	save_Omega.push_back(Omega);
    } 

    // print out occasionally
    if (i%100 == 0) {
      cout << "======== " << i << " =========\n";
      cout << "MCMC:       " << i << "\n";
      cout << "pi          " << pi << "\n";
      cout << "mu          " << mu << "\n";
      // cout << "Omega       " << Omega << "\n\n";
    }
    sample_muOmega();
  }

  Py_END_ALLOW_THREADS

  if (record) {
    // dump stored results to file
    write_matrix("save_probx_" + int2str(k) + "_" + data_file, probx);
    write_vec("save_z_" +  int2str(k) + "_" + data_file, save_z);
    write_vec("save_pi_" + int2str(k) + "_" + data_file, save_pi);
    write_vec_vec("save_mu_" + int2str(k) + "_" + data_file, save_mu);
    write_vec_mat("save_omega_" + int2str(k) + "_" + data_file, save_Omega);
  }

}
