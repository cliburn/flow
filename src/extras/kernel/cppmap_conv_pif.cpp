
#include "conv_pif.hpp"

////////////////////////CONVERT C++ MAP TO AND FROM PYTHON DICTIONARY /////////////////////////

// Convert (C++) map to (Python) dictionary.
template<typename S, typename T> PyObject* cppmap2pydict(map<S,T>& cppdict)
{    
  typename map<S, T>::iterator pos;
  boost::python::dict returndict;
  for(pos = cppdict.begin(); pos != cppdict.end(); pos++)
    returndict[pos->first] = cppdict[pos->first];
  return boost::python::incref(boost::python::object(returndict).ptr());
}

// Convert (Python) dictionary to (C++) map. 
template<typename S, typename T> map<S, T> pydict2cppmap(PyObject* obj)
{    
  map<S, T> cppmap;
  S key;
  T val;
  boost::python::dict pydict(boost::python::borrowed(obj));
  boost::python::list keylst = pydict.keys();
  int keylstlen = extract<int>(keylst.attr("__len__")());

  for(int i=0; i<keylstlen; i++)
    {
      key = extract<S>(keylst[i]);
      val = extract<T>(pydict[keylst[i]]);
      cppmap.insert(std::make_pair(key, val));
    }
  return cppmap;
}

template<typename S, typename T>
struct cppmap_to_python_dict
{
  static PyObject* convert(map<S,T> cppdict)
  {
    return cppmap2pydict<S,T>(cppdict);
  }
};

template<typename S, typename T>
struct cppmap_from_python_dict
{
  cppmap_from_python_dict()
  {
    boost::python::converter::registry::push_back(
						  &convertible,
						  &construct,
						  boost::python::type_id<map<S, T> >());
  }
  
  static void* convertible(PyObject* obj_ptr)
  {
    // if (!PyArray_Check(obj_ptr)) return 0;
    return obj_ptr;
  }
  
  static void construct(
			PyObject* obj_ptr,
			boost::python::converter::rvalue_from_python_stage1_data* data)
  {
    void* storage = (
		     (boost::python::converter::rvalue_from_python_storage<map<S, T> >*)
		     data)->storage.bytes;
    new (storage) map<S, T>(pydict2cppmap<S, T>(obj_ptr));
    data->convertible = storage;
  }
};

void export_cppmap_conv()
{
  boost::python::to_python_converter<map<int, vector<double> >,
    cppmap_to_python_dict<int, vector<double> > >();
  cppmap_from_python_dict<int, vector<double> >();

  boost::python::to_python_converter<map<int, int>,
    cppmap_to_python_dict<int, int> >();
  cppmap_from_python_dict<int, int>();

  boost::python::to_python_converter<map<vector<double>, vector<int> >,
    cppmap_to_python_dict<vector<double>, vector<int> > >();
  cppmap_from_python_dict<vector<double>, vector<int> >();
}
