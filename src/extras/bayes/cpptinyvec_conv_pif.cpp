#include "conv_pif.hpp"


//////////////////// CONVERT BLITZ C++ TINYVECTOR TO AND FROM PYTHON TUPLE //////////////////////////

// Convert (Python) tuple to (C++) Blitz TinyVector.
template<typename T, int N> blitz::TinyVector<T,N> pytuple2cpptinyvec(PyObject* obj)
{
  unsigned int i;
  boost::python::tuple tup(boost::python::borrowed(obj));
  blitz::TinyVector<T,N> vec;
  for(i=0; i<N; i++)
    {
      T lstelemi = extract<T>(tup[i]);
      vec[i] = lstelemi;
    }  
  return vec;
}

// Convert (C++) Blitz TinyVector to (Python) tuple.
template<typename T, int N> PyObject* cpptinyvec2pytuple(blitz::TinyVector<T,N> vec)
{
  boost::python::list lst;
  for(int i=0; i<N; i++)
      lst.append(vec[i]);
  
  return boost::python::incref(boost::python::object(boost::python::tuple(lst)).ptr());
}

template<typename T, int N>
struct cpptinyvec_to_python_tuple
  {
    static PyObject* convert(const blitz::TinyVector<T, N>& vec)
    {
      return cpptinyvec2pytuple(vec);
    }
};

template<typename T, int N>
struct cpptinyvec_from_python_tuple
{
  cpptinyvec_from_python_tuple()
  {
    boost::python::converter::registry::push_back(
						  &convertible,
						  &construct,
						  boost::python::type_id<blitz::TinyVector<T, N> >());
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
		     (boost::python::converter::rvalue_from_python_storage<blitz::TinyVector<T, N> >*)
		     data)->storage.bytes;
    new (storage) blitz::TinyVector<T, N>(pytuple2cpptinyvec<T, N>(obj_ptr));
    data->convertible = storage;
  }
};

void export_cpptinyvec_conv()
{
  boost::python::to_python_converter<blitz::TinyVector<int, 2>, cpptinyvec_to_python_tuple<int, 2> >();
  cpptinyvec_from_python_tuple<int, 2>();

  boost::python::to_python_converter<blitz::TinyVector<int, 3>, cpptinyvec_to_python_tuple<int, 3> >();
  cpptinyvec_from_python_tuple<int, 3>();

  boost::python::to_python_converter<blitz::TinyVector<double, 1>, cpptinyvec_to_python_tuple<double, 1> >();
  cpptinyvec_from_python_tuple<double, 1>();

  boost::python::to_python_converter<blitz::TinyVector<double, 2>, cpptinyvec_to_python_tuple<double, 2> >();
  cpptinyvec_from_python_tuple<double, 2>();

  boost::python::to_python_converter<blitz::TinyVector<double, 3>, cpptinyvec_to_python_tuple<double, 3> >();
  cpptinyvec_from_python_tuple<double, 3>();
}
