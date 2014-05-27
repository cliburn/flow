#include "distributions.hpp"
#include "diagonal_from_vector.hpp"

namespace lapack = boost::numeric::bindings::lapack;

typedef ublas::matrix<double, ublas::column_major> matrix_t;

ublas::vector<double> dirichlet_rnd(const ublas::vector<int>& nz) {
  //! Returns sample from a Dirichlet distribution with dimension k = len(nz).
  int k = nz.size();
  ublas::vector<double> A(k);
  for (int i=0; i<k; ++i) {
    A(i) = Rmath::rgamma(1+nz(i), 1);
  }

  return A/sum(A);
}

ublas::matrix<double> wishart_1(int df, const ublas::matrix<double>& P, const size_t p, const size_t r) {
  // extract common sub-calculation from wishart_rnd etc
  ublas::matrix<double> U(p, r);
  U = ublas::zero_matrix<double>(p, r);
  for (size_t i=0; i<r; ++i) {
    U(i, i) = sqrt(Rmath::rgamma((df-i)/2.0, 2.0));
    for (size_t j=i+1; j<r; ++j) {
      U(i, j) = Rmath::rnorm(0, 1);
    }
  }
  
  U = prod(U, trans(P));
  return prod(trans(U), U);
}  

ublas::matrix<double> wishart_rnd(const int df, ublas::matrix<double>& S) {
  //! Wishart random matrix
  //! does not correct for poorly conditioned matrix 
  size_t p = S.size1();
  ublas::vector<double> D(p);
  ublas::matrix<double> P(p, p);
  ublas::matrix<double> F(p, p);
  F = ublas::zero_matrix<double>(p, p);

  // make copy of S
  // ublas::matrix<double> SS(S);

  lapack::gesvd('A', 'A', S, D, P, F);
  // svd0(S, P, D, F);

  P = prod(trans(P), diagm(ublas::apply_to_all<functor::inv_sqrt<double> >(D)));
  // rprod does not seem any faster than diagonalizing D before multiplication
  // P = rprod(P, ublas::apply_to_all<functor::inv_sqrt<double> >(D));
  
  return wishart_1(df, P, p, p);
}

ublas::vector<ublas::matrix<double> > wishart_rnd(const int df, ublas::matrix<double>& S, const int mc) {
  //! inverse Wishart random matrix
  //! does not correct for poorly conditioned matrix 
  size_t p = S.size1();
  ublas::vector<double> D(p);
  ublas::matrix<double> P(p, p);
  ublas::matrix<double> F(p, p);
  F = ublas::zero_matrix<double>(p, p);

  // make copy of S
  // ublas::matrix<double> SS(S);

  lapack::gesvd('A', 'A', S, D, P, F);
  // svd0(S, P, D, F);
  
  P = prod(trans(P), diagm(ublas::apply_to_all<functor::inv_sqrt<double> >(D)));
  // rprod does not seem any faster than diagonalizing D before multiplication
  // P = rprod(P, ublas::apply_to_all<functor::inv_sqrt<double> >(D));

  // generate mc samples
  ublas::vector<ublas::matrix<double> > K(mc);
  for (int i=0; i<mc; ++i)
    K(i) = wishart_1(df, P, p, p);
  return K;
}

ublas::matrix<double> wishart_InvA_rnd(const int df, ublas::matrix<double>& S) {
  // Generates wishart matrix allowing for singular wishart
  size_t p = S.size1();
  ublas::vector<double> D(p);
  ublas::matrix<double> P(p, p);
  ublas::matrix<double> F(p, p);
  F = ublas::zero_matrix<double>(p, p);

  // make copy of S
  // ublas::matrix<double> SS(S);

  lapack::gesvd('A', 'A', S, D, P, F);
  // P = trans(P);
  // svd0(S, P, D, F);

  //! correct for singular matrix
  std::vector<size_t> ii;
  double max_d = *max_element(D.begin(), D.end());
  for (size_t i=0; i<D.size(); ++i)
    if (D(i) > max_d*1e-9)
      ii.push_back(i);
  
  size_t r = ii.size();
  ublas::indirect_array<> idx(r);
  for (size_t i=0; i<r; ++i)
    idx(i) = ii[i];

  ublas::indirect_array<> irow(p);
  for (size_t i=0; i<p; ++i) 
    irow(i) = i;
  ublas::matrix<double> Q(p, r);
  // Q = prod(project(P, irow, idx), diagm(ublas::apply_to_all<functor::inv_sqrt<double> >(project(D, idx))));
  // rprod does not seem any faster than diagonalizing D before multiplication
  Q = rprod(project(trans(P), irow, idx), ublas::apply_to_all<functor::inv_sqrt<double> >(D));
  // axpy_prod(project(P, irow, idx), diagm(ublas::apply_to_all<functor::inv_sqrt<double> >(project(D, idx))), Q, true);

  return wishart_1(df, Q, p, r);
}

ublas::vector<ublas::matrix<double> > wishart_InvA_rnd(const int df, ublas::matrix<double>& S, const int mc) {
  // Generates wishart matrix allowing for singular wishart
  size_t p = S.size1();
  ublas::vector<double> D(p);
  ublas::matrix<double> P(p, p);
  ublas::matrix<double> F(p, p);
  F = ublas::zero_matrix<double>(p, p);

  // make copy of S
  // ublas::matrix<double> SS(S);

  lapack::gesvd('A', 'A', S, D, P, F);
  // svd0(S, P, D, F);
  // P = trans(P);

  //! correct for singular matrix
  std::vector<size_t> ii;
  for (size_t i=0; i<D.size(); ++i)
    if (D(i) > norm_inf(D)*1e-9)
      ii.push_back(i);
  
  size_t r = ii.size();
  ublas::indirect_array<> idx(r);
  for (size_t i=0; i<r; ++i)
    idx(i) = ii[i];

  ublas::indirect_array<> irow(p);
  for (size_t i=0; i<irow.size(); ++ i) 
    irow(i) = i;
  ublas::matrix<double> Q(p, r);
  // Q = prod(project(P, irow, idx), diagm(ublas::apply_to_all<functor::inv_sqrt<double> >(project(D, idx))));
  // rprod does not seem any faster than diagonalizing D before multiplication
  // Q = rprod(project(P, irow, idx), ublas::apply_to_all<functor::inv_sqrt<double> >(D));
  axpy_prod(project(trans(P), irow, idx), diagm(ublas::apply_to_all<functor::inv_sqrt<double> >(project(D, idx))), Q, true);

  // generate mc samples
  ublas::vector<ublas::matrix<double> > K(mc);
  for (int i=0; i<mc; ++i)
    K(i) = wishart_1(df, Q, p, r);
  return K;
}

double det(const ublas::matrix<double>& M) {
  //! returns fabs(determinant) of M using LU decomposition

  // create a working copy of the input
  ublas::matrix<double> A(M);
  // create a permutation matrix for the LU-factorization
  ublas::permutation_matrix<> pm(A.size1());
  // perform LU-factorization
  ublas::lu_factorize(A, pm);

  double det = 1.0;
  for (size_t i = 0; i < A.size1(); ++i) {
    if (pm(i) != i)
      det *= -1.0;
    det *= A(i,i); 
  }
  return det;
}


ublas::vector<double> mvnormpdf(const ublas::matrix<double>& x, const  ublas::vector<double>& mu, const ublas::matrix<double>& Omega) {
  //! Multivariate normal density
  size_t p = x.size1();
  size_t n = x.size2();
  
  double f = sqrt(det(Omega))/pow(2.0*PI, p/2.0);
  // cout << "O: " << Omega << "\n";
  // cout << "f: " << f << "\n";
  ublas::matrix<double> e(p, n);
  e.assign(x - outer_prod(mu, ublas::scalar_vector<double>(n, 1)));
  e = element_prod(e, prod(Omega, e));

  return ublas::apply_to_all<functor::exp<double> > (-(ublas::matrix_sum(e, 0))/2.0)*f;
}
      

