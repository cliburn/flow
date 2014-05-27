#ifndef COMMON_HPP
#define COMMON_HPP
#define MATHLIB_STANDALONE

// C libraries
#include <cerrno>
#include <climits>
#include <cfloat>
#include <cmath>
#include <cstdlib>

#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>
#include <list>
#include <map>
#include <set>
#include <utility>
#include<iostream>
#include <algorithm>
#include <boost/function.hpp>
#include <boost/shared_ptr.hpp>
#include <boost/tuple/tuple.hpp>
#include <boost/array.hpp>
#include <blitz/array.h>
#include <blitz/tinyvec-et.h>

#include <boost/numeric/ublas/vector_proxy.hpp>
#include <boost/numeric/ublas/triangular.hpp>
#include <boost/numeric/ublas/lu.hpp>
#include <boost/numeric/bindings/traits/ublas_matrix.hpp>
#include <boost/numeric/bindings/traits/std_vector.hpp>
#include <boost/numeric/bindings/traits/ublas_symmetric.hpp>
#include <boost/numeric/ublas/io.hpp> 

#include "utils.hpp"
#include "ublas_utils.hpp"
#include "math_utils.hpp"
#include "cholesky.hpp"
// #include "randutil.hpp"

// C libraries
#include <cerrno>
#include <climits>
#include <cfloat>
#include <cmath>
#include <cstdlib>
#include <ctime>
namespace Rmath
{
#include <Rmath.h>
}

using std::cin;
using std::cout;
using std::cerr;
using std::endl;
using std::string;
using std::vector;
using std::list;
using std::map;
using std::set;
using std::pair;
//using boost::make_tuple;
//using boost::tuple;
using boost::shared_ptr;
using boost::weak_ptr;
using blitz::TinyVector;

typedef boost::function<double (const double&)> distFnPtr;

namespace ublas = boost::numeric::ublas;
using ublas::slice;
using ublas::range;
using ublas::matrix_vector_slice;
using ublas::matrix_vector_range;

const double PI=3.141592653589793238462643;


#endif
