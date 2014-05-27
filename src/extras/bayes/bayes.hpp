#ifndef BAYES_HPP
#define BAYES_HPP

#include "common.hpp"
#include "distributions.hpp"
#include "kmeans.hpp"

class Bayes
{
  // data
  ublas::matrix<double> x;
  int n;
  int p;
  int k;

  // working
  ublas::matrix<double> probx;
  ublas::vector<double> pi;
  ublas::vector<ublas::vector<double> > mu;
  ublas::vector<ublas::matrix<double> > Omega;
  ublas::vector<int> z;

  // max loglik values
  double current;
  double loglik;
  ublas::vector<double> ml_pi;
  ublas::vector<ublas::vector<double> > ml_mu;
  ublas::vector<ublas::matrix<double> > ml_Omega;

  // storage
  std::vector<ublas::vector<int> > save_z;
  std::vector<ublas::vector<double> > save_pi;
  std::vector<ublas::vector<ublas::vector<double> > > save_mu;
  std::vector<ublas::vector<ublas::matrix<double> > > save_Omega;

public:
  // initialize data set x
  void init(const ublas::matrix<double>& _x, const int _n, const int _p, const int _k);

  // accessors
  double get_loglik() const { return loglik; }
  ublas::vector<double> get_ml_pi() const { return ml_pi; }
  ublas::vector<ublas::vector<double> > get_ml_mu() const { return ml_mu; }
  ublas::vector<ublas::matrix<double> > get_ml_Omega() const { return ml_Omega; }

  ublas::matrix<double> get_probx() const { return probx; }
  ublas::vector<double> get_pi() const { return pi; }
  ublas::vector<ublas::vector<double> > get_mu() const { return mu; }
  ublas::vector<ublas::matrix<double> > get_Omega() const { return Omega; }
  ublas::vector<int> get_z() const { return z; }
  ublas::vector<ublas::vector<double> > get_save_pi() const {
    ublas::vector<ublas::vector<double> > tmp;
    tmp.resize(save_pi.size());
    for (unsigned i=0; i<save_pi.size(); ++i)
      tmp[i].resize(save_pi[i].size());
    std::copy(save_pi.begin(), save_pi.end(), tmp.begin());
    return tmp;
    // return save_pi;
  }


  ublas::vector<ublas::vector<ublas::vector<double> > > get_save_mu() const { 
    ublas::vector<ublas::vector<ublas::vector<double> > > tmp;
    tmp.resize(save_mu.size());
    for (unsigned i=0; i<save_mu.size(); ++i) {
      tmp[i].resize(save_mu[i].size());
      for (unsigned j=0; j<save_mu[i].size(); ++j) {
	tmp[i][j].resize(save_mu[i][j].size());
      }
    }
    for (unsigned i=0; i<save_mu.size(); ++i) {
      std::copy(save_mu[i].begin(), save_mu[i].end(), tmp[i].begin());
    }
    return tmp;
    // return save_mu; 
  }


  ublas::vector<ublas::vector<ublas::matrix<double> > > get_save_Omega() const { 
    ublas::vector<ublas::vector<ublas::matrix<double> > > tmp;
    tmp.resize(save_Omega.size());
    for (unsigned i=0; i<save_Omega.size(); ++i) {
      tmp[i].resize(save_Omega[i].size());
      for (unsigned j=0; j<save_Omega[i].size(); ++j) {
	tmp[i][j].resize(save_Omega[i][j].size1(), save_Omega[i][j].size2());
      }
    }
    for (unsigned i=0; i<save_Omega.size(); ++i) 
      for (unsigned j=0; j<save_Omega[i].size(); ++j) {
	tmp[i][j].assign(save_Omega[i][j]);
    }
    return tmp;
    // return save_Omega; 
  }
  ublas::vector<ublas::vector<int> > get_save_z() const { 
    ublas::vector<ublas::vector<int> > tmp;
    tmp.resize(save_z.size());
    for (unsigned i=0; i<save_z.size(); ++i) {
      tmp[i].resize(save_z[i].size());
    }
    for (unsigned i=0; i<save_z.size(); ++i) {
      tmp[i].assign(save_z[i]);
    }
    return tmp;
    // return save_z; 
  }

  // mutators
  void set_pi(ublas::vector<double> _pi) { pi = _pi; }
  void set_mu(ublas::vector<ublas::vector<double> > _mu) { mu = _mu; }
  void set_Omega(ublas::vector<ublas::matrix<double> > _Omega) { Omega = _Omega; }

  // samplers
  void sample_zpi();
  void sample_muOmega();

  // driver
  void mcmc(const int nit, const int nmc, const string& data_file=".out", const bool record=false);
};

#endif
