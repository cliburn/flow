#ifndef RANDUTIL_HPP
#define RANDUTIL_HPP
#define MATHLIB_STANDALONE

// C libraries
#include <cerrno>
#include <climits>
#include <cfloat>
#include <cmath>
#include <cstdlib>

#ifdef RMATH_RAND
namespace Rmath
{
#include <Rmath.h>
}
#endif
#include <ctime>

void set_rseed(const unsigned int& seed1, 
	       const unsigned int& seed2);

void set_state(const unsigned int& seed1 = std::time(NULL), 
	       const unsigned int& seed2 = std::clock());

double msi_runif(const double& a, const double& b);

double msi_rnorm(const double& mean, const double& std_dev);

double msi_rpois(const double& mean);

int rpois(double mu);
#endif
