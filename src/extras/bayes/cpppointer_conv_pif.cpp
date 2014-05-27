#include "conv_pif.hpp"
#include <boost/shared_ptr.hpp>
#include <boost/python/register_ptr_to_python.hpp> 
using boost::shared_ptr;

template<int dim>
void cpppointer_conv()
{
}

void export_cpppointer_conv()
{
  cpppointer_conv<2>();
  cpppointer_conv<3>();
}
