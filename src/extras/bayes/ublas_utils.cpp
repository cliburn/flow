#include "ublas_utils.hpp"
#include <cassert>

/*
namespace boost { namespace numeric { namespace ublas {
  // Linkage for Fortran version of the Lapack routine dpotrf
  // from routine in mat2cpp http://toronto.rfpk.washington.edu/doc/mat2cpp/cholesky.cpp.htm
  matrix<double> cholesky
  (const matrix<double> &x, size_t &rank)
  {    assert( x.size1() == x.size2() );
  size_t i, j;
  
  size_t m = x.size1(); 
  int c_uplo = int('U'); 
  double  *a     = new double  [m * m];
  for(i = 0; i < m; i++)
    {    for(j = 0; j < m; j++)
      a[ i + j * m ] = x(i, j);
    }
  int lda  = int(m);
  int fm   = int(m);
  int info;
  c2dpotrf_ (&c_uplo, &fm, a, &lda, &info);
  
  assert( info >= 0 );
  if( info == 0 )
    rank = m;
  else rank = size_t(info - 1);
  
  matrix<double> z(m, m);
  for(i = 0; i < m; i++)
    {    for(j = i; j < m; j++)
      z(i, j) = a[ i + j * m ];
    for(j = 0; j < i; j++)
      z(i, j) = 0.;
    }
  delete [] a;
  return z;
  }
}}}
*/
