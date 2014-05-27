#include "conv_pif.hpp"
#include <set>
using std::set;

//////////////////// CONVERT C++ SET TO AND FROM PYTHON LIST //////////////////////////////////////////////

// Convert (C++) set of values to (Python) list of values.

template<typename T> PyObject* cppset2pylst(const set<T>& cppset)
{
  T val;
  boost::python::list lst;
  typename set<T>::iterator pos;
  for(pos = cppset.begin(); pos != cppset.end(); pos++)
    {    
      val = *pos;
      lst.append(val);
    }
  return boost::python::incref(boost::python::object(lst).ptr());
}

// Convert (Python) Teger list to (C++) Teger set.
template<typename T>
set<T> pylst2cppset(PyObject* obj)
{
  int i, lstlen;
  T tmp;
  set<T> resultset;
  boost::python::list lst(boost::python::borrowed(obj));
  lstlen = extract<int>(lst.attr("__len__")());
   for(i = 0; i < lstlen; i++)
     {
       tmp = extract<T>(lst[i]);
       resultset.insert(tmp);  
     }  
return resultset;
}

template<typename T>
struct cppset_to_python_list
  {
    static PyObject* convert(const set<T>& clst)
    {
      return cppset2pylst(clst);
    }
};

template<typename T>
struct cppset_from_python_list
{
  cppset_from_python_list()
  {
    boost::python::converter::registry::push_back(
						  &convertible,
						  &construct,
						  boost::python::type_id<set<T> >());
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
		     (boost::python::converter::rvalue_from_python_storage<set<T> >*)
		     data)->storage.bytes;
    new (storage) set<T>(pylst2cppset<T>(obj_ptr));
    data->convertible = storage;
  }
};

void export_cppset_conv()
{
  boost::python::to_python_converter<set<string>, 
    cppset_to_python_list<string> >();
  cppset_from_python_list<string>();
  boost::python::to_python_converter<set<int>, 
    cppset_to_python_list<int> >();
  cppset_from_python_list<int>();
}
