#include "common.hpp"
#include "distributions.hpp"
#include "utils.hpp"
#include "ublas_utils.hpp"
#include "mcmc.hpp"
#include "fixtures.hpp"

/*! 
Usage example:
time ./bayes_main 0 100000 750 3 5 2 /home/cliburn/hg/bayes/data/mcmc_data.txt
time ./bayes_main nit nmc n kmin kmax p data_file <init_file>
*/

typedef ublas::matrix<double, ublas::column_major> matrix_t;

int main(int argc, char* argv[])
{
  // random seed
  set_state();
  //   set_rseed(1, 2);

  int nit = std::atoi(argv[1]);
  int nmc = std::atoi(argv[2]);
  int n = std::atoi(argv[3]);
  int kmin = std::atoi(argv[4]);
  int kmax = std::atoi(argv[5]);
  int p = std::atoi(argv[6]);
  string data_file = argv[7];
  int record = 0;
  string init_file = "";
  if (argc > 8)
    record = atoi(argv[8]);

  // just get filename - remove any directory information
  string::size_type pos = data_file.find_last_of("/");
  string filename = data_file.substr(pos+1);
  for (int k=kmin; k<=kmax; ++k) {
    mcmc_fixture_base f(n, k, p, data_file, init_file);

    mcmc(nit, nmc, f.x, f.n, f.p, f.k, f.pi, f.mu, f.Omega, f.z, filename, record);

    // calc covariance matrix as inverse of precision matrix
    ublas::vector<ublas::matrix<double> > Sigma(f.Omega);
    for (size_t i=0; i<f.Omega.size(); ++i)
      ublas::InvertMatrix(f.Omega(i), Sigma(i));

    cout << "MCMC iters: " << nmc << "\n";
    cout << "pi          " << f.pi << "\n";
    cout << "mu          " << f.mu << "\n";
    cout << "Omega       " << f.Omega << "\n";
    cout << "Sigma       " << Sigma << "\n\n";
  }
}  
