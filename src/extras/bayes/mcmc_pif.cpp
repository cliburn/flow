#include "conv_pif.hpp"
#include "mcmc.hpp"

using namespace boost::python;

void export_mcmc() {
  def("mcmc", mcmc_bp);
}
