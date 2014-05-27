#include "conv_pif.hpp"
#include <boost/shared_ptr.hpp>
#include <boost/python/register_ptr_to_python.hpp> 
using boost::shared_ptr;

#include "analyzer.hpp"

void export_cpppointer_conv()
{
  boost::python::register_ptr_to_python<boost::shared_ptr<Analyzer> >();
}
