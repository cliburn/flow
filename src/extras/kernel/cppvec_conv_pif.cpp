#include "conv_pif.hpp"

////////////// CONVERT C++ VECTOR TO AND FROM PYTHON LIST ///////////////////////////////

// Convert (C++) vector to (Python) tuple as PyObject*.
template<typename T> PyObject* cppvec2pylst(const vector<T>& vec)
{
  unsigned int i;
  boost::python::list lst;
  for(i=0; i<vec.size(); i++)
    lst.append(vec[i]);
  return boost::python::incref(boost::python::object(boost::python::tuple(lst)).ptr());
}

// Convert (Python) tuple to (C++) vector.
template<typename T> vector<T> pylst2cppvec(PyObject* obj)
{
  unsigned int i;
  vector<T> vec;
  boost::python::tuple tup(boost::python::borrowed(obj));
  unsigned int tuplen = extract<int>(tup.attr("__len__")());
  for(i=0; i<tuplen; i++)
    {
      T tupelem = extract<T>(tup[i]);
      vec.push_back(tupelem);
    }  
  return vec;
}

template<typename T>
struct cppvec_to_python_list
  {
    static PyObject* convert(const vector<T>& vec)
    {
      return cppvec2pylst(vec);
    }
};

template<typename T>
struct cppvec_from_python_list
{
  cppvec_from_python_list()
  {
    boost::python::converter::registry::push_back(
						  &convertible,
						  &construct,
						  boost::python::type_id<vector<T> >());
  }
  
  static void* convertible(PyObject* obj_ptr)
  {
    return obj_ptr;
  }
  
  static void construct(
			PyObject* obj_ptr,
			boost::python::converter::rvalue_from_python_stage1_data* data)
  {
    void* storage = (
		     (boost::python::converter::rvalue_from_python_storage<vector<T> >*)
		     data)->storage.bytes;
    new (storage) vector<T>(pylst2cppvec<T>(obj_ptr));
    data->convertible = storage;
  }
};

void export_cppvec_conv()
{
  boost::python::to_python_converter<vector<double>, cppvec_to_python_list<double> >();
  cppvec_from_python_list<double>();

  boost::python::to_python_converter<vector<int>, cppvec_to_python_list<int> >();
  cppvec_from_python_list<int>();

  boost::python::to_python_converter<vector<vector<double> >, cppvec_to_python_list<vector<double> > >();
  cppvec_from_python_list<vector<double> >();

  boost::python::to_python_converter<vector<vector<int> >, cppvec_to_python_list<vector<int> > >();
  cppvec_from_python_list<vector<int> >();
}
