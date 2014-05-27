#include "conv_pif.hpp"

////////////////////////CONVERT BLITZ C++ NUMERIC ARRAY TO AND FROM PYTHON LIST /////////////////////////

/*
NOTE:

These conversion functions are generic for any type (such that the assignment operator works). See 
http://www.oonumerics.org/blitz/docs/blitz_2.html#SEC57 for why an
array of array presents special difficulties, for example.

If speed is desired, then it should be possible to do a template specialization to (for example) the case 
of blitz<double, dim> using the Numeric/Numarray API directly. See 
http://mail.python.org/pipermail/python-list/2005-November/309423.html and
http://ncmi.bcm.tmc.edu/homes/lpeng/projects/eman2py/design.html for
examples of usage.

I've cut and pasted the relevant bits of code at the bottom of this file (commented out).

Faheem Mitha (26th June 2006).

*/

// Convert (Python) Numarray numeric array to (C++) Blitz numerical array.

// template<typename T, int dim>
// blitz::Array<T, dim> pynumarr2cppnumblitzarr(PyObject* obj){}

template<typename T, int dim>
struct pynumarr2cppnumblitzarr;

template<typename T>
struct pynumarr2cppnumblitzarr<T, 2>
{
  blitz::Array<T, 2> operator()(PyObject* obj)
    {
      int i,j;
      boost::python::numeric::array arr(boost::python::borrowed(obj));
      boost::python::tuple dim = extract<boost::python::tuple>(arr.attr("shape"));
      int dim0 = extract<int>(dim[0]);
      int dim1 = extract<int>(dim[1]);
      blitz::Array<T, 2> A(dim0, dim1);
      
      for(i=0; i<dim0; i++)
	for(j=0; j<dim1; j++)
	  A(i, j) = extract<T>(arr[make_tuple(i,j)]);
      return A;
    }
};

template<typename T>
struct pynumarr2cppnumblitzarr<T, 3>
{
  blitz::Array<T, 3> operator()(PyObject* obj)
    {
      boost::python::object arr(boost::python::borrowed(obj));
      boost::python::tuple dim = extract<boost::python::tuple>(arr.attr("shape"));
      int dim0 = extract<int>(dim[0]);
      int dim1 = extract<int>(dim[1]);
      int dim2 = extract<int>(dim[2]);
      blitz::Array<T, 3> A(dim0, dim1, dim2);
      
      for (int i=0; i<dim0; i++)
	for (int j=0; j<dim1; j++)
	  for (int k=0; k<dim2; k++)
	    A(i,j, k) = extract<T>(arr[make_tuple(i, j, k)]);
      
      return A;
    }
};
// Convert (C++) Blitz++ array to (Python) numeric array.

// template<typename T, int dim>
// PyObject * cppnumblitzarr2pynumarr(const blitz::Array<T, dim>& A){}

template<typename T, int dim>
struct cppnumblitzarr2pynumarr;

template<typename T>
struct cppnumblitzarr2pynumarr<T, 2>
{
  PyObject * operator()(const blitz::Array<T, 2>& A)
    {
      int i, j;
      int rows = A.rows();
      int cols = A.cols();
      
      boost::python::list lst;
      boost::python::list rowlst;
      
      // Copy matrix to python list
      for(i=0; i<rows; i++)
	{
	  for(j=0; j<cols; j++)
	    {
	      T Aij = A(i, j);
	      rowlst.append(Aij);
	    }
	  lst.append(rowlst);
	  rowlst = boost::python::list();
	}
      // Convert to numeric array.
      boost::python::numeric::array arr(lst);
      return boost::python::incref(boost::python::object(arr).ptr());
    }
};

template<typename T>
struct cppnumblitzarr2pynumarr<T, 3>
{
  PyObject* operator()(const blitz::Array<T, 3>& A)
  {
    int dim0 = A.rows();
    int dim1 = A.cols();
    int dim2 = A.depth();  
    
    boost::python::list lstdim1, lstdim2, lstdim3;
    
    // Copy matrix to python list
    for (int i=0; i<dim0; i++)
      {
	for (int j=0; j<dim1; j++)
	  {
	    for (int k=0; k<dim2; k++)
	      {
		T Aijk = A(i, j, k);	 
		lstdim1.append(Aijk);
	      }
	    lstdim2.append(lstdim1);	 
	    lstdim1 = boost::python::list();
	  }
	lstdim3.append(lstdim2);     
	lstdim2 = boost::python::list();
      }
    // Convert to numeric array
      boost::python::numeric::array arr(lstdim3);
      return boost::python::incref(boost::python::object(arr).ptr());
  }
}; 

template<typename T, int dim>
struct cppnumblitzarr_to_python_numarr;

template<typename T>
struct cppnumblitzarr_to_python_numarr<T, 2>
{
    static PyObject* convert(blitz::Array<T, 2> const& arr)
    {
      cppnumblitzarr2pynumarr<T, 2> cppnumblitzarr2pynumarrobj;
      return cppnumblitzarr2pynumarrobj(arr);
    }
};

template<typename T>
struct cppnumblitzarr_to_python_numarr<T, 3>
{
    static PyObject* convert(blitz::Array<T, 3> const& arr)
    {
      cppnumblitzarr2pynumarr<T, 3> cppnumblitzarr2pynumarrobj;
      return cppnumblitzarr2pynumarrobj(arr);
    }
};

template<typename T, int dim>
struct cppnumblitzarr_from_python_numarr;

template<typename T>
struct cppnumblitzarr_from_python_numarr<T, 2>
{
  cppnumblitzarr_from_python_numarr()
  {
    boost::python::converter::registry::push_back(
						  &convertible,
						    &construct,
						  boost::python::type_id<blitz::Array<T, 2> >());
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
		     (boost::python::converter::rvalue_from_python_storage<blitz::Array<T, 2> >*)
		     data)->storage.bytes;
    pynumarr2cppnumblitzarr<T, 2> pynumarr2cppnumblitzarrobj;
    new (storage) blitz::Array<T, 2>(pynumarr2cppnumblitzarrobj(obj_ptr));
    data->convertible = storage;
  }
};

template<typename T>
struct cppnumblitzarr_from_python_numarr<T, 3>
{
  cppnumblitzarr_from_python_numarr()
  {
    boost::python::converter::registry::push_back(
						  &convertible,
						    &construct,
						  boost::python::type_id<blitz::Array<T, 3> >());
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
		     (boost::python::converter::rvalue_from_python_storage<blitz::Array<T, 3> >*)
		     data)->storage.bytes;
    pynumarr2cppnumblitzarr<T, 3> pynumarr2cppnumblitzarrobj;
    new (storage) blitz::Array<T, 3>(pynumarr2cppnumblitzarrobj(obj_ptr));
    data->convertible = storage;
  }
};

void export_cppnumblitzarr_conv()
{
  boost::python::to_python_converter<blitz::Array<double, 2>, 
    cppnumblitzarr_to_python_numarr<double, 2> >();
  cppnumblitzarr_from_python_numarr<double, 2>();

  boost::python::to_python_converter<blitz::Array<int, 2>, 
    cppnumblitzarr_to_python_numarr<int, 2> >();
  cppnumblitzarr_from_python_numarr<int, 2>();

  boost::python::to_python_converter<blitz::Array<double, 3>, 
    cppnumblitzarr_to_python_numarr<double, 3> >();
  cppnumblitzarr_from_python_numarr<double, 3>();

  boost::python::to_python_converter<blitz::Array<int, 3>, 
    cppnumblitzarr_to_python_numarr<int, 3> >();
  cppnumblitzarr_from_python_numarr<int, 3>();
}

// (from http://mail.python.org/pipermail/python-list/2005-November/309423.html)
// #ifndef PY_TO_BLITZ_H
// #define PY_TO_BLITZ_H

// #include "Python.h"
// #include "Numeric/arrayobject.h"
// #include "blitz/array.h"

// using namespace blitz;

// // Convert a Numpy array to a blitz one, using the original's data (no copy)
// template<class T, int N>
// static Array<T,N> py_to_blitz(const PyArrayObject* arr_obj)
// {
//     const int T_size = sizeof(T);
//     TinyVector<int,N> shape(0);
//     TinyVector<int,N> strides(0);
//     int *arr_dimensions = arr_obj->dimensions;
//     int *arr_strides = arr_obj->strides;

//     for (int i=0;i<N;++i) {
//         shape[i]   = arr_dimensions[i];
//         strides[i] = arr_strides[i]/T_size;
//     }
//     return Array<T,N>((T*) arr_obj->data,shape,strides,neverDeleteData);
// }
// #endif  // PY_TO_BLITZ_H

// (from http://ncmi.bcm.tmc.edu/homes/lpeng/projects/eman2py/design.html)
// //  foo.h
// class Foo {
// public:
//     PyObject* get_num_array();
// private:
//     float* array;
// };
	       
// // foo.C
// #define PY_ARRAY_UNIQUE_SYMBOL Py_Array_test_foo
// #define NO_IMPORT_ARRAY
// #include "Numeric/arrayobject.h"
		
// PyObject* Foo::get_num_array()		
// {
//     int dims[1];
//     int ndim = 1;
//     int dim = 10;
//     dims[0] = dim;
		
//     PyArrayObject* num_array =
// 	(PyArrayObject *) PyArray_FromDims(ndim, dims, PyArray_FLOAT);
    
//     float* num_array_data = (float*) num_array->data;

//     for (int i = 0; i < dim; i++) {
// 	num_array_data[i] = array[i];
//     }
    
//     return (PyObject*) num_array;
// }
