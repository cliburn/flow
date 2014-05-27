#include "mcmc.hpp"
#include "distributions.hpp"
#include "utils.hpp"
#include "fixtures.hpp"
#include "Python.h"
// #include "diagonal_from_vector.hpp"
// #include "mat2cpp.hpp"

// namespace ublas = boost::numeric::ublas;
// namespace lapack = boost::numeric::bindings::lapack;
// namespace atlas = boost::numeric::bindings::atlas;

void sample_zpi(const ublas::matrix<double>& x, const int n, const int p, const int k, ublas::vector<double>& pi, 
		ublas::vector<ublas::vector<double> >& mu, ublas::vector<ublas::matrix<double> >& Omega, ublas::vector<int>& z)
  //! sample classification
{
  ublas::matrix<double> probx(k, n);
  for (int i=0; i<k; ++i) {
    row(probx, i).assign(pi(i) * mvnormpdf(x, mu(i), Omega(i)));
  }

  ublas::vector<int> nz(k);
  for (int i=0; i<k; ++i)
    nz(i) = 0;

  for (int i=0; i<n; ++i) {
    column(probx, i) /= sum(column(probx, i));
    z(i) = rdisc(column(probx, i));
  }

  for (int i=0; i<k; ++i)
    for (int j=0; j<n; ++j)
      if (z[j] == i)
	nz(i) += 1;

  pi = dirichlet_rnd(nz);

  // cout << "nz " << nz << "\n";
  // cout << "pi " << pi << "\n";

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

void sample_muOmega(const ublas::matrix<double>& x, const int p, const int k, 
		    ublas::vector<ublas::vector<double> >& mu, ublas::vector<ublas::matrix<double> >& Omega, const ublas::vector<int>& z) {
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

      // ublas::symmetric_adaptor<ublas::matrix<double>, ublas::upper> SH(Omega(j));
      SH.assign(Omega(j));
      // atlas::potrf(SH);
      cholesky_decompose(SH, L);
      Omega_inv.assign(solve(SH, I, ublas::upper_tag()));
      //       ublas::InvertMatrix(mat2cpp::cholesky(Omega(j), rank), Omega_inv);
      mu(j).assign(a*n_idx*m + sqrt(a)*prod(Omega_inv, Rmath::rnorm(0, 1, p)));
    } else {
      // Omega(j).assign(wishart_rnd(d0, S0));
      Omega(j).assign(wishart_InvA_rnd(d0, S0));

      // ublas::symmetric_adaptor<ublas::matrix<double>, ublas::upper> SH(Omega(j));
      SH.assign(Omega(j));
      // atlas::potrf(SH);
      cholesky_decompose(SH, L);
      Omega_inv.assign(solve(SH, I, ublas::upper_tag()));
      //       ublas::InvertMatrix(mat2cpp::cholesky(Omega(j), rank), Omega_inv);
      mu(j).assign(sqrt(tau) * prod(Omega_inv, Rmath::rnorm(0, 1, p)));
    }
  }
}

void mcmc(const int nit, const int nmc, const ublas::matrix<double>& x, const int n, const int p, const int k, 
	  ublas::vector<double>& pi, ublas::vector<ublas::vector<double> >& mu, 
	  ublas::vector<ublas::matrix<double> >& Omega, ublas::vector<int>& z,
	  const string& data_file, const bool record) {

  // storage
  std::vector<ublas::vector<int> > save_z;
  std::vector<ublas::vector<double> > save_pi;
  std::vector<ublas::vector<ublas::vector<double> > > save_mu;
  std::vector<ublas::vector<ublas::matrix<double> > > save_omega;

  Py_BEGIN_ALLOW_THREADS

  //! MCMC routine
  for (int i=0; i<(nit + nmc); ++i) {
    sample_zpi(x, n, p, k, pi, mu, Omega, z);

    // save MCMC samples
    if (record) {
      if (i >= nit) {
	save_z.push_back(z);
	save_pi.push_back(pi);
	save_mu.push_back(mu);
	save_omega.push_back(Omega);
      }
    }

    // print z on last iteration
    //     if ((i+1) == (nit+nmc)) 
    //       for (unsigned ii=0; ii<z.size(); ++ii)
    // 	cout << z[ii] << " ";

    // print out occasionally
    if (i%100 == 0) {
      cout << "======== " << i << " =========\n";
      cout << "MCMC:       " << i << "\n";
      cout << "pi          " << pi << "\n";
      cout << "mu          " << mu << "\n";
      // cout << "Omega       " << Omega << "\n\n";
    }
    sample_muOmega(x, p, k, mu, Omega, z);
  }

  Py_END_ALLOW_THREADS

  if (record) {
    // dump stored results to file
    write_vec("results/save_z_" +  int2str(k) + "_" + data_file, save_z);
    write_vec("results/save_pi_" + int2str(k) + "_" + data_file, save_pi);
    write_vec_vec("results/save_mu_" + int2str(k) + "_" + data_file, save_mu);
    write_vec_mat("results/save_omega_" + int2str(k) + "_" + data_file, save_omega);
  }
}
 
// boost python version - cannot have non-const args
void mcmc_bp(const int nit, const int nmc, const ublas::matrix<double>& x, const int n, const int p, const int k, const bool record) {
  ublas::vector<double> pi;
  ublas::vector<ublas::vector<double> > mu;
  ublas::vector<ublas::matrix<double> > Omega;
  ublas::vector<int> z;

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
  
  // assign random indices to z
  z.resize(n);
  for (size_t i=0; i<z.size(); ++i)
    z(i) = std::rand() % k;

  mcmc(nit, nmc, x, n, p, k, pi, mu, Omega, z, ".out", record);
}

