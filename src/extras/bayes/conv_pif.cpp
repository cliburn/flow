#include "conv_pif.hpp"
#include "reaction.hpp"
#include "solfac.hpp"
#include "cell.hpp"

// // Convert (C++) hash table to (Python) dictionary.
// template<typename S, typename T> boost::python::dict cpphashtab2pydict(hash_map<S,T>& cppdict)
// {
//   typename hash_map<S, T>::iterator pos;
//   boost::python::dict returndict;
//   for(pos = cppdict.begin(); pos != cppdict.end(); pos++)
//     returndict[pos->first] = cppdict[pos->first];
  
//   return returndict;
// }

// // Convert (C++) hash table to (Python) dictionary as PyObject*.
// template<typename S, typename T> PyObject* cpphashtab2pydictobj(hash_map<S,T>& cppdict)
// {    
//   boost::python::dict returndict = cpphashtab2pydict<S, T>(cppdict);
//   return boost::python::incref(boost::python::object(returndict).ptr());
// }

// template<typename S, typename T>
// struct cpphashtab_to_python_dict
// {
//   static PyObject* convert(hash_map<S,T> cppdict)
//   {
//     return cpphashtab2pydictobj<S,T>(cppdict);
//   }
// };

TinyVector<double, 3> foo(const TinyVector<double, 3>& x)
{
  return x;
}

vector<TinyVector<double, 3> > bar(const vector<TinyVector<double, 3> >& x)
{
  return x;
}

void export_conv_cc()
{

  boost::python::def("foo", foo);
  boost::python::def("bar", bar);

}
