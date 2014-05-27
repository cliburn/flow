#include "conv_pif.hpp"
#include <boost/function.hpp>

void boost_function_pif(const char* boost_function_name)
{

  boost::python::class_<  boost::function<int ()> >
    (boost_function_name, boost::python::init<>())
    .def("__call__", &boost::function<int ()>::operator())
    ;
}

void export_boost_function()
{
 boost_function_pif("boost_function");
}
