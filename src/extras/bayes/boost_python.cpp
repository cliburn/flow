#include "hello.hpp"
#include <boost/python.hpp>
using namespace boost::python;

BOOST_PYTHON_MODULE(hello)
{
  def("greet", greet);
}
