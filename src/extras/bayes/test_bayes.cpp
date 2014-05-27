#include "common.hpp"
#include "distributions.hpp"
#include "utils.hpp"
#include "mcmc.hpp"
#include "kmeans.hpp"
#include "fixtures.hpp"
#include "diagonal_from_vector.hpp"
#include "cholesky.hpp"
#include <boost/test/unit_test.hpp>
// namespace lapack = boost::numeric::bindings::lapack;

using boost::unit_test::test_suite;

mcmc_fixture f;
// typedef ublas::matrix<double, ublas::column_major> matrix_t;

void test_kmeans() {
  int n = 750;
  int p = 2;
  int k = 3;

  ublas::matrix<double> data(p, n);
  data = read_data("../data/mcmc_data.txt", n, p);

  cout << kmeans(data, n, k, p, 1e-6) << "\n";
}  

void test_ublas() {
  ublas::matrix<double> A (3, 2);
  for (unsigned i=0; i<A.size1(); ++i)
    for (unsigned j=0; j<A.size2(); ++j)
      A(i, j) = i*j + j;
  
  ublas::matrix<double> B (2, 3);
  for (unsigned i=0; i<B.size1(); ++i)
    for (unsigned j=0; j<B.size2(); ++j)
      B(i, j) = i+j;

  // check matrix multiplication
  ublas::matrix<double> C (3, 3);
  C(0, 0) = 1; C(0, 1) = 2; C(0, 2) = 3;
  C(1, 0) = 2; C(1, 1) = 4; C(1, 2) = 6;
  C(2, 0) = 3; C(2, 1) = 6; C(2, 2) = 9;
  BOOST_CHECK(norm_inf(prod(A, B) - C) < 1e-6);

  // check element-wise multiplication
  ublas::matrix<double> D(3, 2);
  D(0, 0) = 0; D(0, 1) = 1;
  D(1, 0) = 0; D(1, 1) = 4;
  D(2, 0) = 0; D(2, 1) = 9;
  BOOST_CHECK(norm_inf(element_prod(A, trans(B)) - D) < 1e-6);

  // a vector of matrices
  ublas::vector<ublas::matrix<double> > vofm;
  // allocate a vector of 2 matrices
  vofm.resize(2);
  // allocate matrices A and D to the vector
  vofm(0) = A;
  vofm(1) = D;
  // test accessing matrices from vector in an expression
  BOOST_CHECK(norm_inf(element_prod(vofm(0), trans(B)) - vofm(1)) < 1e-6);

  // test indexing of vector
  ublas::indirect_array<> idx(3);
  idx(0) = 3; idx(1) = 1; idx(2) = 5;
  ublas::vector<double> V(10);
  for (size_t i=0; i<V.size(); ++i)
    V[i] = i;
  ublas::vector<double> VV(3);
  VV(0) = 3; VV(1) = 1; VV(2) = 5;
  BOOST_CHECK(norm_inf(VV - project(V, idx)) == 0);

  // test arbitrary sized indexing of vector
  std::vector<unsigned> ii;
  ii.push_back(3);
  ii.push_back(1);
  ii.push_back(5);
  ublas::indirect_array<> jj(ii.size());
  for (unsigned i=0; i<ii.size(); ++i)
    jj(i) = ii[i];
  BOOST_CHECK(norm_inf(VV - project(V, jj)) == 0);

  // test indexing of matrix
  ublas::indirect_array<> irow(2), icol(2);
  irow(0) = 1; irow(1) = 0;
  icol(0) = 2; icol(1) = 1;
  ublas::matrix_indirect<ublas::matrix<double> > Ci(C, irow, icol);
  Ci = project(C, irow, icol);
  
  ublas::matrix<double> CC(2, 2);
  CC(0, 0) = C(1, 2); CC(0, 1) = C(1, 1);
  CC(1, 0) = C(0, 2); CC(1, 1) = C(0, 1);
  BOOST_CHECK(norm_inf(Ci - CC) == 0);

  // test use of proxies
  // check rows
  ublas::vector<double> ans(3);
  for (size_t i=0; i<3; ++i) {
    ans(0) = C(i, 0); ans(1) = C(i, 1); ans(2) = C(i, 2);
    BOOST_CHECK(norm_inf(matrix_vector_slice<ublas::matrix<double> > (C, slice(i, 0, 3), slice(0, 1, 3)) - ans) < 1e-6);
  }

  // check cols
  for (size_t i=0; i<3; ++i) {
    ans(0) = C(0, i); ans(1) = C(1, i); ans(2) = C(2, i);
    BOOST_CHECK(norm_inf(matrix_vector_slice<ublas::matrix<double> > (C, slice(0, 1, 3), slice(i, 0, 3)) - ans) < 1e-6);
  }

  // check matrix_sum
  ublas::matrix<double> x(2, 10);
  for (int i=0; i<2; ++i)
    for (int j=0; j<10; ++j)
      x(i, j) = i*10+j;

  ublas::vector<double> ans_row(10);
  ans_row(0) = 10; ans_row(1) = 12; ans_row(2) = 14; ans_row(3) = 16; ans_row(4) = 18;
  ans_row(5) = 20; ans_row(6) = 22; ans_row(7) = 24; ans_row(8) = 26; ans_row(9) = 28;
  BOOST_CHECK(norm_inf(ublas::matrix_sum<double>(x, 0) - ans_row) == 0);

  ublas::vector<double> ans_col(2);
  ans_col(0) = 45; ans_col(1) = 145;
  BOOST_CHECK(norm_inf(ublas::matrix_sum<double>(x, 1) - ans_col) == 0);

  // check that outer(u, u) and trans(U)*U give same answer
  ublas::vector<double> u(3);
  ublas::matrix<double> U(1, 3);
  u(0) = 3; u(1) = 4; u(2) = 5;
  U(0, 0) = 3; U(0, 1) = 4; U(0, 2) = 5;
  BOOST_CHECK(norm_inf(outer_prod(u, u) - prod(trans(U), U)) == 0);
}    

/*
void test_cholesky() {
  ublas::matrix<double> H (3, 3);
  ublas::triangular_matrix<double, ublas::upper> U (3, 3);
  H(0,0) = 1.00000; H(0,1) = 0.50000; H(0,2) = 0.33333;
  H(1,0) = 0.50000; H(1,1) = 0.33333; H(1,2) = 0.25000;
  H(2,0) = 0.33333; H(2,1) = 0.25000; H(2,2) = 0.20000;
  
  size_t rank;
  ublas::matrix<double> U1 = ublas::cholesky(H, rank);

  ublas::symmetric_adaptor<ublas::matrix<double>, ublas::upper> SH(H);
  atlas::potrf(SH);
  U.assign(SH);

  // check that both cholesky factorizations give same results
  cout << U << "\n" << U1 << "\n";
  BOOST_CHECK(norm_inf(U1 - U) == 0);

  // expected results
  ublas::matrix<double> A (3, 3);
  A(0,0) = 1.00000; A(0,1) = 0.50000;  A(0,2) = 0.33333;
  A(1,0) = 0.0;     A(1,1) = 0.288669; A(1,2) = 0.288687;
  A(2,0) = 0.0;     A(2,1) = 0.0;      A(2,2) = 0.0745058;

  BOOST_CHECK(norm_inf(U - A) < 1e-3);

  H(0, 0) = 3; H(0, 1) = 2; H(0, 2) = 1;
  H(1, 0) = 2; H(1, 1) = 2; H(1, 2) = 1;
  H(2, 0) = 1; H(2, 1) = 1; H(2, 2) = 1;
  
  SH.assign(H);
  atlas::potrf(SH);
  U.assign(SH);
  // U = ublas::cholesky(H, rank);
  A(0,0) = 1.73205; A(0,1) = 1.1547;   A(0,2) = 0.57735;
  A(1,0) = 0.0;     A(1,1) = 0.816497; A(1,2) = 0.408248;
  A(2,0) = 0.0;     A(2,1) = 0.0;      A(2,2) = 0.707107;
  BOOST_CHECK(norm_inf(U - A) < 1e-3);
}
*/

void test_cholesky_factor() {
  typedef ublas::matrix<double> m_t;
  typedef ublas::symmetric_adaptor<m_t, ublas::lower> symm_t;

  m_t H(3, 3);

  H(0,0) = 1.00000; H(0,1) = 0.50000; H(0,2) = 0.33333;
  H(1,0) = 0.50000; H(1,1) = 0.33333; H(1,2) = 0.25000;
  H(2,0) = 0.33333; H(2,1) = 0.25000; H(2,2) = 0.20000;

  symm_t SH(H);

  // replace atlas::potrf(SH) with cholesky_decompose(SH, L)
  // note that the answer is now in L, not SH as before
  //   atlas::potrf(SH);
  //   cout << "chol " << SH << "\n";
  ublas::triangular_matrix<double, ublas::lower, ublas::row_major> L (3, 3);
  cholesky_decompose(SH, L);
  cout << "chol2 " << L << "\n";
}

void test_svd() {
  matrix_t H (3, 3);
  H(0,0) = 1.00000; H(0,1) = 0.50000; H(0,2) = 0.33333;
  H(1,0) = 0.50000; H(1,1) = 0.33333; H(1,2) = 0.25000;
  H(2,0) = 0.33333; H(2,1) = 0.25000; H(2,2) = 0.20000;
  
  matrix_t U (3, 3);
  ublas::vector<double> s(3);
  matrix_t VT (3, 3);

  lapack::gesvd('A', 'A', H, s, U, VT);

  // expected results
  matrix_t UU (3, 3);
  UU(0,0) = -0.82704; UU(0,1) =  0.54745; UU(0,2) = 0.12766;
  UU(1,0) = -0.45986; UU(1,1) = -0.52829; UU(1,2) = -0.71375;
  UU(2,0) = -0.32330; UU(2,1) = -0.64901; UU(2,2) = 0.68867;

  ublas::vector<double> SS(3);
  SS(0) = 1.40832; SS(1) = 0.12233; SS(2) = 0.00269;

  BOOST_CHECK(norm_inf(UU - U) < 1e-3);
  BOOST_CHECK(norm_inf(trans(VT) - UU) < 1e-3);
  BOOST_CHECK(norm_inf(SS - s) < 1e-3);
} 


void test_rprod() {
  matrix_t S (3, 3);
  S(0,0) = 1.00000; S(0,1) = 0.50000; S(0,2) = 0.33333;
  S(1,0) = 0.50000; S(1,1) = 0.33333; S(1,2) = 0.25000;
  S(2,0) = 0.33333; S(2,1) = 0.25000; S(2,2) = 0.20000;

  matrix_t P (3, 3);
  ublas::vector<double> D(3);
  matrix_t F (3, 3);

  lapack::gesvd('A', 'A', S, D, P, F);
  
  BOOST_CHECK(norm_inf(prod(P, diagm(ublas::apply_to_all<functor::inv_sqrt<double> >(D))) -
		       rprod(P, ublas::apply_to_all<functor::inv_sqrt<double> >(D))) == 0);
}

void test_dirichlet() {
  //! Test dirichlet random number generator
  ublas::vector<int> nz(3);
  nz[0] = 16;
  nz[1] = 2;
  nz[2] = 2;
  int k = 3;
  int n = 10000;
  ublas::vector<double> result(k);
  for (unsigned i=0; i<result.size(); ++i) {
    result[i] = 0.0;
  }
  
  for (int i=0; i<n; ++i) {
    result += dirichlet_rnd(nz);
  }
  double result_sum = sum(result);
  
  ublas::vector<double> ans(k);
  ans[0] = 17.0/23;
  ans[1] = 3.0/23;
  ans[2] = 3.0/23;
  BOOST_CHECK(norm_inf(result/result_sum - ans) < 1e-3);
}

void test_wishart() {
  //! Test wishart random number generator
  int d = 2; // number of dimensions
  int n = 5; // number of samples
  ublas::matrix<double> V(d, d);
  V(0, 0) = 3.0;
  V(0, 1) = 0.0;
  V(1, 0) = 0.0;
  V(1, 1) = 3.0;
  ublas::matrix<double> result(d, d);

  ublas::matrix<double> ans(d, d);
  ans(0, 0) = 1/3.0;  ans(0, 1) = 0;
  ans(1, 0) = 0;      ans(1, 1) = 1/3.0;
  
  int mc = 1000;
  ublas::vector<ublas::matrix<double> > K;
  // or can replace with wishart_InvA_rnd(n, n*V, mc)
  V *= n;
  K = wishart_rnd(n, V, mc);
  ublas::matrix<double> tmp(d, d);
  tmp = ublas::zero_matrix<double> (d, d);
  for (size_t i=0; i<K.size(); ++ i)
    tmp += K[i];
  // check that mean of mc samples gives expected value
  BOOST_CHECK(norm_inf(tmp/mc - ans) < 0.05);

  unsigned seed1 = 23;
  unsigned seed2 = 47;

  ublas::matrix<double> S(2, 2);
  ublas::matrix<double> S1;
  ublas::matrix<double> S2;
  ublas::vector<ublas::matrix<double> > VS1;
  ublas::vector<ublas::matrix<double> > VS2;

  set_rseed(seed1, seed2);
  S(0, 0) = 87.8310; S(0, 1) = 86.8310;
  S(1, 0) = 86.8310; S(1, 1) = 87.8310;
  VS1 = wishart_rnd(11, S, 1);

  set_rseed(seed1, seed2);
  S(0, 0) = 87.8310; S(0, 1) = 86.8310;
  S(1, 0) = 86.8310; S(1, 1) = 87.8310;
  VS2 = wishart_InvA_rnd(11, S, 1);
  
  set_rseed(seed1, seed2);
  S(0, 0) = 87.8310; S(0, 1) = 86.8310;
  S(1, 0) = 86.8310; S(1, 1) = 87.8310;
  S1 = wishart_rnd(11, S);

  set_rseed(seed1, seed2);
  S(0, 0) = 87.8310; S(0, 1) = 86.8310;
  S(1, 0) = 86.8310; S(1, 1) = 87.8310;
  S2 = wishart_InvA_rnd(11, S);
  
  // check that all forms give same answer
  BOOST_CHECK(norm_inf(VS1(0) - VS2(0)) == 0);
  BOOST_CHECK(norm_inf(S1 - S2) == 0);
  BOOST_CHECK(norm_inf(VS1(0) - S1) == 0);
  BOOST_CHECK(norm_inf(VS2(0) - S2) == 0);
}

void test_wishart_stats() {
  ublas::matrix<double> H(3, 3);
  H(0,0) = 1.00000; H(0,1) = 0.50000; H(0,2) = 0.33333;
  H(1,0) = 0.50000; H(1,1) = 0.33333; H(1,2) = 0.25000;
  H(2,0) = 0.33333; H(2,1) = 0.25000; H(2,2) = 0.20000;

  set_rseed(123, 234);
  ublas::vector<ublas::matrix<double> > v(10);
  for (int i=0; i<10; ++i)
    v(i) = wishart_InvA_rnd(5, H);
  
  for (int i=0; i<10; ++i)
    cout << v(i) << "\n";
}

void test_det() {
  matrix_t A(2, 2);
  A(0, 0) = 3; A(0, 1) = 5;
  A(1, 0) = 2; A(1, 1) = 7;
  BOOST_CHECK(det(A) - 11 < 1e-6);

  ublas::matrix<double> B(3, 3);
  for (int i=0; i<3; ++i)
    for (int j=0; j<3; ++j)
      B(i, j) = i*3+j+1;
  cout << "det(B) " << det(B) << "\n";
  
}

void test_mvnormpdf() {
  matrix_t x(2, 3);
  for (size_t i=0; i<x.size1(); ++i)
    for (size_t j=0; j<x.size2(); ++j)
      x(i, j) = i*x.size2()+j;

  ublas::vector<double> mu(2);
  mu(0) = 2; mu(1) = 1;

  matrix_t Omega(2, 2);
  Omega(0, 0) = 3;   Omega(0, 1) = 0.1;
  Omega(1, 0) = 0.1; Omega(1, 1) = 3;
  
  // check against matlab answer
  ublas::vector<double> ans(x.size2());
  ans(0) = 0.43740524600678e-6;   ans(1) = 0.01970475745536e-6;   ans(2) = 0.00000180149231e-6;
  BOOST_CHECK(norm_inf(mvnormpdf(x, mu, Omega) - ans) < 1e-5);
}

void test_rdisc() {
  int n = 100000;
  ublas::vector<int> results(n);
  ublas::vector<double> p(3);
  p(0) = 0.2; p(1) = 0.3; p(2) = 0.5;
  results = rdisc(n, p);

  double mu0 = 0.0;
  double mu1 = 0.0;
  double mu2 = 0.0;
  for (size_t i=0; i<results.size(); ++i) {
    switch(results(i)) {
    case 0:
      mu0 += 1;
      break;
    case 1:
      mu1 += 1;
      break;
    case 2:
      mu2 += 1;
      break;
    default:
      cout << "Index Error: " << results[i] << "\n";
    }
  }
  BOOST_ASSERT(mu0/n - p(0) < 1e-2);
  BOOST_ASSERT(mu1/n - p(1) < 1e-2);
  BOOST_ASSERT(mu2/n - p(2) < 1e-2);
}

void test_rng() {
  int n = 100000;
  BOOST_CHECK(sum(Rmath::runif(0, 1, n))/n - 0.5 < 1e-3);
}

void test_invert_matrix() {
  ublas::matrix<double> I(3, 3);
  I.assign(ublas::identity_matrix<double> (3,3));

  ublas::matrix<double> A(3, 3);
  A(0, 0) = 1; A(0, 1) = 1; A(0, 2) = 3;
  A(1, 0) = 1; A(1, 1) = 2; A(1, 2) = 3;
  A(2, 0) = 1; A(2, 1) = 1; A(2, 2) = 4; 

  ublas::matrix<double> result(3, 3);
  ublas::InvertMatrix(A, result);

  ublas::matrix<double> ans(3, 3);
  ans(0, 0) = 5; ans(0, 1) = -1; ans(0, 2) = -3;
  ans(1, 0) = -1; ans(1, 1) = 1; ans(1, 2) = 0;
  ans(2, 0) = -1; ans(2, 1) = 0; ans(2, 2) = 1; 

  BOOST_CHECK(norm_inf(result - ans) < 1e-6);

  ublas::matrix<double> H (3, 3);
  ublas::matrix<double> IH (3, 3);

  H(0, 0) = 3; H(0, 1) = 2; H(0, 2) = 1;
  H(1, 0) = 2; H(1, 1) = 2; H(1, 2) = 1;
  H(2, 0) = 1; H(2, 1) = 1; H(2, 2) = 1;

  // ublas::InvertMatrix(ublas::cholesky(H, rank), IH);
  ublas::symmetric_adaptor<ublas::matrix<double>, ublas::upper> SH(H);
  // replace atlas::potrf(SH) with cholesky_decompose(SH, L)
  // note that the answer is now in L, not SH as before
  // potrf computes the Cholesky factorisation of a symmetric or Hermitian positive definite n-by-n matrix A.
  //   atlas::potrf(SH); 
  //   IH.assign(solve(SH, I, ublas::lower_tag() ));
  ublas::triangular_matrix<double, ublas::lower, ublas::row_major> L (3, 3);
  cholesky_decompose(SH, L);
  IH.assign(solve(L, I, ublas::lower_tag() ));

  ans(0, 0) = 0.57735026918963; ans(0, 1) = -0.81649658092773; ans(0, 2) = 0;
  ans(1, 0) = 0;                ans(1, 1) = 1.22474487139159;  ans(1, 2) = -0.70710678118655;
  ans(2, 0) = 0;                ans(2, 1) = 0;                 ans(2, 2) = 1.41421356237309;

  BOOST_CHECK(norm_inf(trans(IH) - ans) < 1e-6);
}

void test_argsort() {
  ublas::vector<double> x(5);
  x(0) = 3; x(1) = 1; x(2) = 0; x(3) = 4; x(4) = 2;
  std::vector<int> idx(argsort(x));
  std::vector<int> ans(5);
  ans[0] = 2; ans[1] = 1; ans[2] = 4; ans[3] = 0; ans[4] = 3;
  for (unsigned i=0; i<idx.size(); ++i)
    BOOST_CHECK(idx[i] == ans[i]);
}

void test_find_all() {
  ublas::vector<int> x(12);
  x(0) = 3; x(1) = 1; x(2) = 0; x(3) = 4; x(4) = 2; x(5) = 1;
  x(6) = 3; x(7) = 1; x(8) = 0; x(9) = 4; x(10) = 2; x(11) = 1;
  std::vector<int> idx(find_all(x, 1));
  std::vector<int> ans(4);
  ans[0] = 1; ans[1] = 5; ans[2] = 7; ans[3] = 11;
  for (unsigned i=0; i<idx.size(); ++i)
    BOOST_CHECK(idx[i] == ans[i]);
}

void test_kron() {
  // use kron for matrix replication
  ublas::matrix<double> u(2, 1);
  u(0, 0) = 1; u(1, 0) = 2;
  ublas::matrix<double> v(2, 5);
  for (int i=0; i<2; ++i)
    for (int j=0; j<5; ++j)
      v(i, j) = u(i, 0);

  BOOST_CHECK(norm_inf(kron(ublas::scalar_matrix<double>(1, 5, 1), u) - v) == 0);
}

void test_sample_zpi() {
  //! doesn't do much - just check that it runs
  // ! output is tested in test_mcmc
  mcmc_fixture f;  
  sample_zpi(f.x, f.n, f.p, f.k, f.pi, f.mu, f.Omega, f.z);
  
  ublas::vector<double> pi_ans(f.k);
  pi_ans(0) = 500.0/750; pi_ans(1) = 150.0/750; pi_ans(2) = 100.0/750;

  BOOST_CHECK(norm_inf(f.pi - pi_ans) < 0.2);
}

void test_sample_muOmega() {
  //! doesn't do much - just check that it runs
  // ! output is tested in test_mcmc
  sample_zpi(f.x, f.n, f.p, f.k, f.pi, f.mu, f.Omega, f.z);
  sample_muOmega(f.x, f.p, f.k, f.mu, f.Omega, f.z);
  
}

void test_read_data() {
  int n = 750;
  int p = 2;
  
  ublas::matrix<double> x(p, 10);
  x = project(read_data("../data/mcmc_data.txt", n, p), range(0, p), range(0, 10));
  
  ublas::matrix<double> data(2, 10);
  data(0, 0) = 10.7033; data(0, 1) = 10.3889; data(0, 2) = 8.38694; data(0, 3) = 9.05769; data(0, 4) = 10.3797; 
  data(0, 5) = 8.5904; data(0, 6) = 11.2813; data(0, 7) = 10.5503; data(0, 8) = 11.6957; data(0, 9) = 11.8225;
  data(1, 0) = 7.03563; data(1, 1) = 8.43726; data(1, 2) = 8.89564; data(1, 3) = 8.3995; data(1, 4) = 11.356; 
  data(1, 5) = 8.29566; data(1, 6) = 10.5883; data(1, 7) = 6.01141; data(1, 8) = 9.09258; data(1, 9) = 10.5418;

  BOOST_CHECK(norm_inf(x-data) < 1e-3);  
}

/* moved to test_mcmc.cpp
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
*/

test_suite*
init_unit_test_suite(int, char* []) {
  test_suite* test = BOOST_TEST_SUITE("test_bayes");

  test->add(BOOST_TEST_CASE(&test_ublas), 0);
  test->add(BOOST_TEST_CASE(&test_dirichlet), 0);
  test->add(BOOST_TEST_CASE(&test_svd), 0);
  test->add(BOOST_TEST_CASE(&test_rprod), 0);
  // test->add(BOOST_TEST_CASE(&test_cholesky), 0);
  test->add(BOOST_TEST_CASE(&test_cholesky_factor), 0);
  test->add(BOOST_TEST_CASE(&test_det), 0);
  test->add(BOOST_TEST_CASE(&test_mvnormpdf), 0);
  test->add(BOOST_TEST_CASE(&test_rdisc), 0);
  test->add(BOOST_TEST_CASE(&test_rng), 0);
  test->add(BOOST_TEST_CASE(&test_invert_matrix), 0);
  test->add(BOOST_TEST_CASE(&test_argsort), 0);
  test->add(BOOST_TEST_CASE(&test_find_all), 0);
  test->add(BOOST_TEST_CASE(&test_kron), 0);
  test->add(BOOST_TEST_CASE(&test_read_data), 0);
  // test->add(BOOST_TEST_CASE(&test_write_data), 0);
  test->add(BOOST_TEST_CASE(&test_sample_zpi), 0);
  test->add(BOOST_TEST_CASE(&test_sample_muOmega), 0);
  test->add(BOOST_TEST_CASE(&test_wishart), 0);
  test->add(BOOST_TEST_CASE(&test_wishart_stats), 0);
  // test->add(BOOST_TEST_CASE(&test_mcmc), 0);
  test->add(BOOST_TEST_CASE(&test_kmeans), 0);

  return test;
}
