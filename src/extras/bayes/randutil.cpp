#include "randutil.hpp"
#include <boost/random/uniform_real.hpp>
#include <boost/random/normal_distribution.hpp>
#include <boost/random/poisson_distribution.hpp>
#include <boost/random/variate_generator.hpp>
#include <boost/random/mersenne_twister.hpp>
#include <string>

using std::string;

namespace
{
  typedef boost::mt19937 base_generator_type;
  base_generator_type generator(42u);
  
  typedef boost::uniform_real<> unif_distribution_type;
  unif_distribution_type unif01_dist(0, 1);
  boost::variate_generator<base_generator_type&, unif_distribution_type> 
  unif01_gen(generator, unif01_dist);
  
  typedef boost::normal_distribution<> normal_distribution_type;
  normal_distribution_type normal01_dist(0, 1);
  boost::variate_generator<base_generator_type&, normal_distribution_type> 
  normal01_gen(generator, normal01_dist);
  
  typedef boost::poisson_distribution<> poisson_distribution_type;

  poisson_distribution_type poisson1_dist(1);
  boost::variate_generator<base_generator_type&, poisson_distribution_type> 
  poisson1_gen(generator, poisson1_dist);
  
  int is_initialized = 0;
}

string randlib_type()
{
#ifdef RMATH_RAND
  return "RMATH_RAND";
#elif BOOST_RAND
  return "BOOST_RAND";
#endif
}

// Set seed in C++ code using seed values.
void set_rseed(const unsigned int& seed1, const unsigned int& seed2)
{
#ifdef RMATH_RAND
  Rmath::set_seed(seed1, seed2);
#elif BOOST_RAND
  generator.seed(seed1);
#endif
}
// Set seed in C++ code using seed values.
void set_state(const unsigned int& seed1, const unsigned int& seed2)
{
  if(is_initialized)
    ;
  else
    {
#ifdef RMATH_RAND
      Rmath::set_seed(seed1, seed2);
#elif BOOST_RAND
      //generator.seed(static_cast<unsigned int>(std::time(seed1)));
      generator.seed(seed1);
#endif
      is_initialized = 1;
    }
}

double msi_runif(const double& a, const double& b)
{
#ifdef RMATH_RAND
  return Rmath::runif(a, b);
#elif BOOST_RAND
  if(a == 0 && b == 1)
    return unif01_gen();
  else
    {
      unif_distribution_type unif_dist(a, b);
      boost::variate_generator<base_generator_type&, unif_distribution_type> 
	unif_gen(generator, unif_dist);
      return unif_gen();
    }
#endif
}

double msi_rnorm(const double& mean, const double& std_dev)
{
#ifdef RMATH_RAND
  return Rmath::rnorm(mean, std_dev);
#elif BOOST_RAND
  if(mean == 0 && std_dev == 1)
    return normal01_gen();
  else
    {
      normal_distribution_type normal_dist(mean, std_dev);
      boost::variate_generator<base_generator_type&, normal_distribution_type> 
	normal_gen(generator, normal_dist);
      return normal_gen();
    }
#endif
}

double msi_rpois(const double& mean)
{
#ifdef RMATH_RAND
  return Rmath::rpois(mean);
#elif BOOST_RAND
  if(mean == 1)
    return poisson1_gen();
  else
    {
      poisson_distribution_type poisson_dist(1);
      boost::variate_generator<base_generator_type&, poisson_distribution_type> 
	poisson_gen(generator, poisson_dist);
      return poisson_gen();
    }
#endif
}

int rpois(double mu)
{
  return static_cast<int>(msi_rpois(mu));
}

