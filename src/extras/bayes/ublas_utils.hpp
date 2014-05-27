#ifndef UBLAS_UTILS_HPP
#define UBLAS_UTILS_HPP

#include "math_common.hpp"
#include "common.hpp"
#include <cassert>

/*****************************************************************

Put generalizations of ublas here. Good candidates include
vector_sum -> e.g. log_min, mean, var
norm_inf -> e.g  other reductions

Some of these may already be in /usr/include/boost/numeric/ublas/functional.hpp

*****************************************************************/

/*
namespace boost { namespace numeric { namespace ublas {
  // Linkage for Fortran version of the Lapack routine dpotrf
  // from routine in mat2cpp http://toronto.rfpk.washington.edu/doc/mat2cpp/cholesky.cpp.htm
  extern matrix<double> cholesky
  (const matrix<double> &x, size_t &rank);

  extern "C" void c2dpotrf_(
			    int   *c_uplo, 
			    int   *n, 
			    double    *a, 
			    int   *lda, 
			    int   *info
			    );
  matrix<double> cholesky (const matrix<double> &x, size_t &rank);
}}}
*/

namespace boost { namespace numeric { namespace ublas { 
  template<class OP, class E>
  BOOST_UBLAS_INLINE
  typename ublas::vector_unary_traits<E, OP>::result_type
  apply_to_all (const ublas::vector_expression<E> &e, const OP& op = OP()) {
    typedef typename ublas::vector_unary_traits<E, OP>::expression_type expression_type;
    return expression_type (e ());
  }
}}}

namespace functor {
  template <class T>
  class sqrt
  {
  public:
    typedef T value_type;
    typedef T result_type;
    sqrt() {}
    
    static
    result_type apply(const value_type& x)
    {
      return std::sqrt(x);
    }
  };

  template <class T>
  class inv_sqrt
  {
  public:
    typedef T value_type;
    typedef T result_type;
    inv_sqrt() {}
    
    static
    result_type apply(const value_type& x)
    {
      return 1.0/std::sqrt(x);
    }
  };

  template <class T>
  class exp
  {
  public:
    typedef T value_type;
    typedef T result_type;
    exp() {}
    
    static
    result_type apply(const value_type& x)
    {
      return std::exp(x);
    }
  };

}

namespace boost { namespace numeric { namespace ublas { 
  /* Matrix inversion routine.
     Uses lu_factorize and lu_substitute in uBLAS to invert a matrix */
  template<class T>
  bool InvertMatrix (const ublas::matrix<T>& input, ublas::matrix<T>& inverse) {
    using namespace boost::numeric::ublas;
    typedef permutation_matrix<std::size_t> pmatrix;
    // create a working copy of the input
    matrix<T> A(input);
    // create a permutation matrix for the LU-factorization
    pmatrix pm(A.size1());

    int res = lu_factorize(A,pm);
    if( res != 0 ) return false;
    
    // create identity matrix of "inverse"
    inverse.assign(ublas::identity_matrix<T>(A.size1()));
    
    // backsubstitute to get the inverse
    lu_substitute(A, pm, inverse);
    
    return true;
  }
}}}

namespace boost { namespace numeric { namespace ublas { 
  /* sum matrix by row or column */
  template<class T>
  // ublas::matrix<T> matrix_sum(ublas::matrix<T>& m, int index) {
  ublas::vector<T> matrix_sum(const ublas::matrix<T>& m, int index) {
    using namespace boost::numeric::ublas;
    ublas::vector<T> result;
    if (index == 0) {
      result.resize(m.size2());
      for (size_t i=0; i<m.size2(); ++i)
	result(i) = sum(column(m, i));
    }
    else if (index == 1) {
      result.resize(m.size1());
      for (size_t i=0; i<m.size1(); ++i)
	result(i) = sum(row(m, i));
    }
    return result;
  }
}}}

namespace boost { namespace numeric { namespace ublas { 
  /// Kronecker tensor product of matrices - as per Matlab kron
  template<typename Matrix_S, typename Matrix_T >
  const
  Matrix_T
    kron(const Matrix_S& lhs, const Matrix_T& rhs)
    {
      typedef typename Matrix_S::size_type matrix_index_s;
      typedef typename Matrix_T::size_type matrix_index_t;
      const matrix_index_s lhs_s1 = lhs.size1();
      const matrix_index_s lhs_s2 = lhs.size2();
      const matrix_index_t rhs_s1 = rhs.size1();
      const matrix_index_t rhs_s2 = rhs.size2();
      Matrix_T result(lhs_s1*rhs_s1, lhs_s2*rhs_s2);
      typedef typename Matrix_S::value_type Scalar_S;
      typedef typename Matrix_S::const_iterator1 const_iteratorS1;
      typedef typename Matrix_S::const_iterator2 const_iteratorS2;
      typedef typename Matrix_T::value_type Scalar_T;
      typedef typename Matrix_T::const_iterator1 const_iterator1;
      typedef typename Matrix_T::const_iterator2 const_iterator2;
      for (const_iteratorS1
	     lhs_it1 = lhs.begin1();
	   lhs_it1 != lhs.end1();
	   ++lhs_it1)
	for (const_iteratorS2
	       lhs_it2 = lhs_it1.begin();
	     lhs_it2 != lhs_it1.end();
	     ++lhs_it2)
	  {
	    const matrix_index_t start1 = rhs_s1 * lhs_it2.index1();
	    const matrix_index_t start2 = rhs_s2 * lhs_it2.index2();
	    const Scalar_S& lhs_val = (*lhs_it2);
	    for (const_iterator1
		   rhs_it1 = rhs.begin1();
		 rhs_it1 != rhs.end1();
		 ++rhs_it1)
	      for (const_iterator2
		     rhs_it2 = rhs_it1.begin();
		   rhs_it2 != rhs_it1.end();
		   ++rhs_it2)
		result(start1 + rhs_it2.index1(), start2 + rhs_it2.index2()) = lhs_val * *rhs_it2;
	  }
      return result;
    }
}}}
  
#endif
