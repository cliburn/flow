#include "conv_pif.hpp"
#include "analyzer.hpp"

struct Analyzer_wrap: Analyzer, boost::python::wrapper<Analyzer>
{
  Analyzer_wrap(vector<vector<double> > _data, int _dim, int _n, 
		int _k, double _h, double _alpha):
  Analyzer(_data, _dim, _n, _k, _h, _alpha){}

  vector<double> mean_shift(vector<double> x)
  {
    return this->get_override("mean_shift")();
  }

  double density(vector<double> x)
  {
    return (this->get_override("density")()).as<double>();
  }
};

void export_analyzer()
{
  boost::python::class_<Analyzer_wrap, boost::noncopyable>
    ("Analyzer", boost::python::init<vector<vector<double> >, int, int, int, double, double>())
    .def("find_seeds", &Analyzer::find_seeds)
    .def("find_seeds_simple", &Analyzer::find_seeds_simple)
    .def("mean_shift", boost::python::pure_virtual(&Analyzer::mean_shift))
    .def("density", boost::python::pure_virtual(&Analyzer::density))
    .def("dip_test", &Analyzer::dip_test)
    .def("find_modes", &Analyzer::find_modes)
    .def("norm", &Analyzer::norm)
    .def("euclid_dist", &Analyzer::euclid_dist)
    .def("merge_modes", &Analyzer::merge_modes)
    .def("find_nbrs", &Analyzer::find_nbrs)
    .def("check_modes", &Analyzer::check_modes)
    .def("pop_check_modes", &Analyzer::pop_check_modes)
    .def("get_h", &Analyzer::get_h)
    .def("set_h", &Analyzer::set_h)
    .def("calc_h", &Analyzer::calc_h)
    ;
  boost::python::class_<Uniform_Analyzer, boost::python::bases<Analyzer> >
    ("Uniform_Analyzer", boost::python::init<vector<vector<double> >, int, int, int, double, double>())
    .def("mean_shift", &Uniform_Analyzer::mean_shift)
    .def("density", &Uniform_Analyzer::density)
    ;
  boost::python::class_<Epanechnikov_Analyzer, boost::python::bases<Analyzer> >
    ("Epanechnikov_Analyzer", boost::python::init<vector<vector<double> >, int, int, int, double, double>())
    .def("mean_shift", &Epanechnikov_Analyzer::mean_shift)
    .def("density", &Epanechnikov_Analyzer::density)
    ;
}
