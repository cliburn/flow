#include "conv_pif.hpp"

////////////////////////CONVERT BLITZ C++ PAIR TO AND FROM PYTHON LIST /////////////////////////

// Convert (C++) pair to (Python) tuple as PyObject*.
template<typename T1, typename T2> PyObject* cpppair2pytuple(const std::pair<T1, T2>& p)
{
  boost::python::list lst;
  lst.append(p.first);
  lst.append(p.second);
  return boost::python::incref(boost::python::object(boost::python::tuple(lst)).ptr());
}

// Convert (Python) tuple to (C++) pair.
template<typename T1, typename T2> std::pair<T1, T2> pytuple2cpppair(PyObject* obj)
{
  std::pair<T1, T2> p;
  boost::python::tuple tup(boost::python::borrowed(obj));
  p.first = extract<T1>(tup[0]);
  p.second = extract<T2>(tup[1]);
  return p;
}

template<typename T1, typename T2>
struct cpppair_to_python_tuple
{
  static PyObject* convert(const std::pair<T1, T2>& p)
    {
      return cpppair2pytuple<T1, T2>(p);
    }
};

template<typename T1, typename T2>
struct cpppair_from_python_tuple
{
  cpppair_from_python_tuple()
  {
    boost::python::converter::registry::push_back(
						  &convertible,
						  &construct,
						  boost::python::type_id<std::pair<T1, T2> >());
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
    //    const char* value = PyString_AsString(obj_ptr);
    // if (value == 0) boost::python::throw_error_already_set();
    void* storage = (
		     (boost::python::converter::rvalue_from_python_storage<std::pair<T1, T2> >*)
		     data)->storage.bytes;
    new (storage) std::pair<T1, T2>(pytuple2cpppair<T1, T2>(obj_ptr));
    data->convertible = storage;
  }
};

void export_cpppair_conv()
{
  boost::python::to_python_converter<std::pair<string, int>, cpppair_to_python_tuple<string, int> >();
  cpppair_from_python_tuple<string, int>();
  boost::python::to_python_converter<std::pair<int, int>, cpppair_to_python_tuple<int, int> >();
  cpppair_from_python_tuple<int, int>();
}
