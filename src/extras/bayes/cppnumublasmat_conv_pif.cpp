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

// Convert (Python) Numarray numeric array to (C++) Ublas matrix.

// template<typename T, int dim>
// ublas::matrix<T, dim> pynumarr2cppnumublasmat(PyObject* obj){}

template<typename T>
struct pynumarr2cppnumublasmat
{
  ublas::matrix<T> operator()(PyObject* obj)
    {
      int i,j;
      boost::python::numeric::array arr(boost::python::borrowed(obj));
      boost::python::tuple dim = extract<boost::python::tuple>(arr.attr("shape"));
      int dim0 = extract<int>(dim[0]);
      int dim1 = extract<int>(dim[1]);
      ublas::matrix<T> A(dim0, dim1);
      
      for(i=0; i<dim0; i++)
	for(j=0; j<dim1; j++)
	  A(i, j) = extract<T>(arr[make_tuple(i,j)]);
      return A;
    }
};

// Convert (C++) Blitz++ array to (Python) numeric array.

// template<typename T, int dim>
// PyObject * cppnumublasmat2pynumarr(const ublas::matrix<T, dim>& A){}

template<typename T>
struct cppnumublasmat2pynumarr
{
  PyObject * operator()(const ublas::matrix<T>& A)
    {
      int i, j;
      int rows = A.size1();
      int cols = A.size2();
      
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
struct cppnumublasmat_to_python_numarr
{
    static PyObject* convert(ublas::matrix<T> const& arr)
    {
      cppnumublasmat2pynumarr<T> cppnumublasmat2pynumarrobj;
      return cppnumublasmat2pynumarrobj(arr);
    }
};

template<typename T>
struct cppnumublasmat_from_python_numarr
{
  cppnumublasmat_from_python_numarr()
  {
    boost::python::converter::registry::push_back(
						  &convertible,
						    &construct,
						  boost::python::type_id<ublas::matrix<T> >());
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
		     (boost::python::converter::rvalue_from_python_storage<ublas::matrix<T> >*)
		     data)->storage.bytes;
    pynumarr2cppnumublasmat<T> pynumarr2cppnumublasmatobj;
    new (storage) ublas::matrix<T>(pynumarr2cppnumublasmatobj(obj_ptr));
    data->convertible = storage;
  }
};

void export_cppnumublasmat_conv()
{
  boost::python::to_python_converter<ublas::matrix<double>, 
    cppnumublasmat_to_python_numarr<double> >();
  cppnumublasmat_from_python_numarr<double>();

  boost::python::to_python_converter<ublas::matrix<int>, 
    cppnumublasmat_to_python_numarr<int> >();
  cppnumublasmat_from_python_numarr<int>();
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
