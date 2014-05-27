#include "conv_pif.hpp"

template<int dim>
class Cell;

//////////////////// CONVERT C++ LIST TO AND FROM PYTHON LIST //////////////////////////////////////////////

// Convert (C++) list to (Python) list as PyObject*.
template<typename T> PyObject* cpplst2pylst(const list<T>& clst)
{
  boost::python::list lst;
  for(typename list<T>::const_iterator pos=clst.begin(); pos != clst.end(); pos++)
    lst.append(*pos);
  return boost::python::incref(boost::python::object(lst).ptr());
}

// Convert (Python) list to (C++) list.
template<typename T> list<T> pylst2cpplst(PyObject* obj)
{
  unsigned int i;
  list<T> clst;
  boost::python::list lst(boost::python::borrowed(obj));
  unsigned int lstlen = extract<int>(lst.attr("__len__")());
  for(i=0; i<lstlen; i++)
    {
      T lstelem = extract<T>(lst[i]);
      clst.push_back(lstelem);
    }  
  return clst;
}

template<typename T>
struct cpplst_to_python_list
  {
    static PyObject* convert(const list<T>& clst)
    {
      return cpplst2pylst(clst);
    }
};

template<typename T>
struct cpplst_from_python_list
{
  cpplst_from_python_list()
  {
    boost::python::converter::registry::push_back(
						  &convertible,
						  &construct,
						  boost::python::type_id<list<T> >());
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
		     (boost::python::converter::rvalue_from_python_storage<list<T> >*)
		     data)->storage.bytes;
    new (storage) list<T>(pylst2cpplst<T>(obj_ptr));
    data->convertible = storage;
  }
};

void export_cpplist_conv()
{
  boost::python::to_python_converter<list<int>, 
    cpplst_to_python_list<int> >();
  cpplst_from_python_list<int>();

  boost::python::to_python_converter<list<shared_ptr<Cell<2> > >, 
    cpplst_to_python_list<shared_ptr<Cell<2> > > >();
  cpplst_from_python_list<shared_ptr<Cell<2> > >();

  boost::python::to_python_converter<list<shared_ptr<Cell<3> > >, 
    cpplst_to_python_list<shared_ptr<Cell<3> > > >();
  cpplst_from_python_list<shared_ptr<Cell<3> > >();

  boost::python::to_python_converter<list<boost::array<int, 2> >, 
    cpplst_to_python_list<boost::array<int, 2> > >();
  cpplst_from_python_list<boost::array<int, 2> >();

  boost::python::to_python_converter<list<boost::array<int, 3> >, 
    cpplst_to_python_list<boost::array<int, 3> > >();
  cpplst_from_python_list<boost::array<int, 3> >();
}
