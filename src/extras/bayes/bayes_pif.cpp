#include "conv_pif.hpp"
#include "bayes.hpp"
#include "pifmod.hpp"

using namespace boost::python;

void export_bayes() {
  class_<Bayes>("Bayes", init<>())
    .def("init", &Bayes::init)
    .def("get_loglik", &Bayes::get_loglik)
    .def("get_ml_pi", &Bayes::get_ml_pi)
    .def("get_ml_mu", &Bayes::get_ml_mu)
    .def("get_ml_Omega", &Bayes::get_ml_Omega)
    .def("get_probx", &Bayes::get_probx)
    .def("get_pi", &Bayes::get_pi)
    .def("get_mu", &Bayes::get_mu)
    .def("get_Omega", &Bayes::get_Omega)
    .def("get_z", &Bayes::get_z)
    .def("get_save_pi", &Bayes::get_save_pi)
    .def("get_save_mu", &Bayes::get_save_mu)
    .def("get_save_Omega", &Bayes::get_save_Omega)
    .def("get_save_z", &Bayes::get_save_z)
    .def("set_pi", &Bayes::set_pi)
    .def("set_mu", &Bayes::set_mu)
    .def("set_Omega", &Bayes::set_Omega)
    .def("sample_zpi", &Bayes::sample_zpi)
    .def("sample_muOmega", &Bayes::sample_muOmega)
    .def("mcmc", &Bayes::mcmc)
    ;
}

BOOST_PYTHON_MODULE(bayes)
{
  export_bayes();

  export_cpparr_conv();
  export_cpplist_conv();
  export_cppmap_conv();
  export_cppnumublasmat_conv();
  export_cppnumublasvec_conv();
  export_cpppair_conv();
  export_cpppointer_conv();
  export_cppset_conv();
  export_cpptinyvec_conv();
  export_cppvec_conv();
}
