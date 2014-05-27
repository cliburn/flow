#include "conv_pif.hpp"

////////////////////////// CONVERT C++ BOOST ARRAY TO AND FROM PYTHON LIST /////////////////////////////////

// Convert (C++) Boost Array to (Python) list as PyObject*.
template<typename T, int dim> PyObject* cpparr2pytuple(const boost::array<T, dim>& arr)
{
  boost::python::list lst;
  for(int i=0; i<dim; i++)
    lst.append(arr[i]);
  return boost::python::incref(boost::python::object(boost::python::tuple(lst)).ptr());
}


// Convert (Python) list to (C++) list.
template<typename T, int dim> boost::array<T, dim> pytuple2cpparr(PyObject* obj)
{
  unsigned int i;
  boost::array<T, dim> arr;
  boost::python::tuple tup(boost::python::borrowed(obj));
  unsigned int tuplen = extract<int>(tup.attr("__len__")());
  for(i=0; i<tuplen; i++)
    {
      T tupelem = extract<T>(tup[i]);
      arr[i] = tupelem;
    }  
  return arr;
}

template<typename T, int dim>
struct cpparr_to_python_tuple
{
    static PyObject* convert(const boost::array<T, dim>& arr)
    {
      return cpparr2pytuple<T, dim>(arr);
    }
};

template<typename T, int dim>
struct cpparr_from_python_tuple
{
  cpparr_from_python_tuple()
  {
    boost::python::converter::registry::push_back(
						  &convertible,
						  &construct,
						  boost::python::type_id<boost::array<T, dim> >());
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
		     (boost::python::converter::rvalue_from_python_storage<boost::array<T, dim> >*)
		     data)->storage.bytes;
    new (storage) boost::array<T, dim>(pytuple2cpparr<T, dim>(obj_ptr));
    data->convertible = storage;
  }
};

void export_cpparr_conv()
{
  boost::python::to_python_converter<boost::array<int, 2>, cpparr_to_python_tuple<int, 2> >();
  cpparr_from_python_tuple<int, 2>();

  boost::python::to_python_converter<boost::array<int, 3>, cpparr_to_python_tuple<int, 3> >();
  cpparr_from_python_tuple<int, 3>();

  boost::python::to_python_converter<boost::array<double, 2>, cpparr_to_python_tuple<double, 2> >();
  cpparr_from_python_tuple<double, 2>();

  boost::python::to_python_converter<boost::array<double, 3>, cpparr_to_python_tuple<double, 3> >();
  cpparr_from_python_tuple<double, 3>();

  boost::python::to_python_converter<boost::array<double, 4>, cpparr_to_python_tuple<double, 4> >();
  cpparr_from_python_tuple<double, 4>();

  boost::python::to_python_converter<boost::array<double, 6>, cpparr_to_python_tuple<double, 6> >();
  cpparr_from_python_tuple<double, 6>();
}
