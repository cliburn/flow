#include "conv_pif.hpp"
#include "label.hpp"

void export_label()
{  
  boost::python::def("create_analyzer", create_analyzer);
  boost::python::def("find_majority", find_majority);
  boost::python::def("label_seeds", label_seeds);
  boost::python::def("label_points", label_points);
}
