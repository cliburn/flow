#ifndef MCMC_HPP
#define MCMC_HPP

#include "common.hpp"

void sample_zpi(const ublas::matrix<double>& x, const int n, const int p, const int k, ublas::vector<double>& pi, 
		ublas::vector<ublas::vector<double> >& mu, ublas::vector<ublas::matrix<double> >& Omega, ublas::vector<int>& z);

void sample_muOmega(const ublas::matrix<double>& x, const int p, const int k, 
		    ublas::vector<ublas::vector<double> >& mu, ublas::vector<ublas::matrix<double> >& Omega, const ublas::vector<int>& z);

void mcmc(const int nit, const int nmc, const ublas::matrix<double>& x, const int n, const int p, const int k, 
	  ublas::vector<double>& pi, ublas::vector<ublas::vector<double> >& mu, 
	  ublas::vector<ublas::matrix<double> >& Omega, ublas::vector<int>& z,
	  const string& data_file=".out", const bool record=false);

void mcmc_bp(const int nit, const int nmc, const ublas::matrix<double>& x, const int n, const int p, const int k, const bool record);

#endif
