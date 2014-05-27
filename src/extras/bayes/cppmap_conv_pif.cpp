
#include "conv_pif.hpp"
////////////////////////CONVERT C++ MAP (DEFAULT SORT FUNCTION) TO AND FROM PYTHON DICTIONARY //////////////

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
      // WARNING; This fails if a default-constructed object of T
      // cannot be assigned to by arbitary objects of T.
      // See specialization for blitz Array.
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


////////////////////////CONVERT C++ MAP (BLITZ ARRAY IS VALUE) TO AND FROM PYTHON DICTIONARY //////////////

// Convert (C++) map to (Python) dictionary.
template<typename S, typename T, int dim> PyObject* cppbmap2pydict(map<S, blitz::Array<T, dim> >& cppdict)
{    
  typename map<S, blitz::Array<T, dim> >::iterator pos;
  boost::python::dict returndict;
  for(pos = cppdict.begin(); pos != cppdict.end(); pos++)
    returndict[pos->first] = cppdict[pos->first];
  return boost::python::incref(boost::python::object(returndict).ptr());
}

// Convert (Python) dictionary to (C++) map. 
template<typename S, typename T, int dim> map<S, blitz::Array<T, dim> > pydict2cppbmap(PyObject* obj)
{    
  map<S, blitz::Array<T, dim> > cppmap;
  S key;
  boost::python::dict pydict(boost::python::borrowed(obj));
  boost::python::list keylst = pydict.keys();
  int keylstlen = extract<int>(keylst.attr("__len__")());
  // Extract shape of Blitz array from map.
  boost::python::numeric::array arr = extract<boost::python::numeric::array>(pydict[keylst[0]]);
  boost::python::tuple tup = extract<boost::python::tuple>(arr.getshape());
  TinyVector<T, dim> sh;
  for(int i=0; i<dim; i++)
    sh[i] = extract<T>(tup[i]);
  blitz::Array<T, dim> val(sh);

  for(int i=0; i<keylstlen; i++)
    {
      key = extract<S>(keylst[i]);
      val = extract<blitz::Array<T, dim> >(pydict[keylst[i]]);
      cppmap.insert(std::make_pair(key, val));
    }
  return cppmap;
}

template<typename S, typename T, int dim>
struct cppbmap_to_python_dict
{
  static PyObject* convert(map<S, blitz::Array<T, dim> > cppdict)
  {
    return cppbmap2pydict<S, T, dim>(cppdict);
  }
};

template<typename S, typename T, int dim>
struct cppbmap_from_python_dict
{
  cppbmap_from_python_dict()
  {
    boost::python::converter::registry::push_back(
						  &convertible,
						  &construct,
						  boost::python::type_id<map<S, blitz::Array<T, dim> > >());
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
		     (boost::python::converter::rvalue_from_python_storage<map<S, blitz::Array<T, dim> > >*)
		     data)->storage.bytes;
    new (storage) map<S, blitz::Array<T, dim> >(pydict2cppbmap<S, T, dim>(obj_ptr));
    data->convertible = storage;
  }
};

////////////////////////CONVERT C++ MAP TO AND FROM PYTHON DICTIONARY //////////////


// Convert (C++) map to (Python) dictionary.
template<typename S, typename T, typename C> PyObject* cppmapc2pydict(map<S,T,C>& cppdict)
{    
  typename map<S, T, C>::iterator pos;
  boost::python::dict returndict;
  for(pos = cppdict.begin(); pos != cppdict.end(); pos++)
    returndict[pos->first] = cppdict[pos->first];
  return boost::python::incref(boost::python::object(returndict).ptr());
}

// Convert (Python) dictionary to (C++) map. 
template<typename S, typename T, typename C> map<S, T, C> pydict2cppmapc(PyObject* obj)
{    
  map<S, T, C> cppmap;
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

template<typename S, typename T, typename C>
struct cppmapc_to_python_dict
{
  static PyObject* convert(map<S,T,C> cppdict)
  {
    return cppmapc2pydict<S,T,C>(cppdict);
  }
};

template<typename S, typename T, typename C>
struct cppmapc_from_python_dict
{
  cppmapc_from_python_dict()
  {
    boost::python::converter::registry::push_back(
						  &convertible,
						  &construct,
						  boost::python::type_id<map<S, T, C> >());
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
		     (boost::python::converter::rvalue_from_python_storage<map<S, T, C> >*)
		     data)->storage.bytes;
    new (storage) map<S, T, C>(pydict2cppmapc<S, T, C>(obj_ptr));
    data->convertible = storage;
  }
};

////////////////////////////////////////////////////////////////////////////////////////////////

void export_cppmap_conv()
{
  boost::python::to_python_converter<map<string, int>, 
    cppmap_to_python_dict<string, int> >();
  cppmap_from_python_dict<string, int>();
  
  boost::python::to_python_converter<map<string, double>, 
    cppmap_to_python_dict<string, double> >();
  cppmap_from_python_dict<string, double>();
  
  boost::python::to_python_converter<map<int, TinyVector<double, 2> >, 
    cppmap_to_python_dict<int, TinyVector<double, 2> > >();
  cppmap_from_python_dict<int, TinyVector<double, 2> >();
    
  boost::python::to_python_converter<map<int, TinyVector<double, 3> >, 
    cppmap_to_python_dict<int, TinyVector<double, 3> > >();
  cppmap_from_python_dict<int, TinyVector<double, 3> >();
  
  boost::python::to_python_converter<map<double, map<int, TinyVector<double, 2> > >, 
    cppmap_to_python_dict<double, map<int, TinyVector<double, 2> > > >();
  cppmap_from_python_dict<double, map<int, TinyVector<double, 2> > >();
  
  boost::python::to_python_converter<map<double, map<int, TinyVector<double, 3> > >, 
    cppmap_to_python_dict<double, map<int, TinyVector<double, 3> > > >();
  cppmap_from_python_dict<double, map<int, TinyVector<double, 3> > >();
  
  boost::python::to_python_converter<map<boost::array<int, 2>, int>, 
    cppmap_to_python_dict<boost::array<int, 2>, int> >();
  cppmap_from_python_dict<boost::array<int, 2>, int>();

  boost::python::to_python_converter<map<boost::array<int, 3>, int>, 
    cppmap_to_python_dict<boost::array<int, 3>, int> >();
  cppmap_from_python_dict<boost::array<int, 3>, int>();

  boost::python::to_python_converter<map<string, blitz::Array<double, 2> >,
    cppbmap_to_python_dict<string, double, 2> >();
  cppbmap_from_python_dict<string, double, 2>();

  boost::python::to_python_converter<map<string, blitz::Array<double, 3> >,
    cppbmap_to_python_dict<string, double, 3> >();
  cppbmap_from_python_dict<string, double, 3>();

  boost::python::to_python_converter<map<string, vector<double> >,
    cppmap_to_python_dict<string, vector<double> > >();
  cppmap_from_python_dict<string, vector<double> >();
}
