#ifndef _BOOST_UBLAS_DIAGONAL_FROM_VECTOR_
#define _BOOST_UBLAS_DIAGONAL_FROM_VECTOR_

// create by James Knight 10/18/2006
// diagonal_vector_adaptor is a modified version of banded_adaptor in banded.hpp

#include <boost/numeric/ublas/matrix.hpp>
#include <boost/numeric/ublas/matrix_proxy.hpp>
#include <boost/numeric/ublas/detail/temporary.hpp>

// Iterators based on ideas of Jeremy Siek

namespace boost { namespace numeric { namespace ublas {


  template<class M>
  class diagonal_vector_adaptor :
    public matrix_expression<diagonal_vector_adaptor<M> > {
    
    typedef diagonal_vector_adaptor<M> self_type;
  public:
#ifdef BOOST_UBLAS_ENABLE_PROXY_SHORTCUTS
    using matrix_expression<self_type>::operator ();
#endif
    typedef const M const_matrix_type;
    typedef M matrix_type;
    typedef typename M::size_type size_type;
    typedef typename M::difference_type difference_type;
    typedef typename M::value_type value_type;
    typedef typename M::const_reference const_reference;
    typedef typename boost::mpl::if_<boost::is_const<M>,
				     typename M::const_reference,
				     typename M::reference>::type reference;
    typedef typename boost::mpl::if_<boost::is_const<M>,
				     typename M::const_closure_type,
				     typename M::closure_type>::type matrix_closure_type;
    typedef const self_type const_closure_type;
    typedef self_type closure_type;
    // Replaced by _temporary_traits to avoid type requirements on M
    //typedef typename M::vector_temporary_type vector_temporary_type;
    //typedef typename M::matrix_temporary_type matrix_temporary_type;
    typedef typename storage_restrict_traits<typename M::storage_category,
					     packed_proxy_tag>::storage_category storage_category;
    
    // Construction and destruction
    BOOST_UBLAS_INLINE
    diagonal_vector_adaptor(matrix_type &data):
      matrix_expression<self_type> (),
      data_ (data), lower_ (0), upper_ (0) {}
    BOOST_UBLAS_INLINE
    diagonal_vector_adaptor (const diagonal_vector_adaptor &m):
      matrix_expression<self_type> (),
      data_ (m.data_), lower_ (m.lower_), upper_ (m.upper_) {}

    // Accessors
    BOOST_UBLAS_INLINE
    size_type size1 () const {
      return data_.size ();
    }
    BOOST_UBLAS_INLINE
    size_type size2 () const {
      return data_.size ();
    }
    BOOST_UBLAS_INLINE
    size_type lower () const {
      return size_type();
    }
    BOOST_UBLAS_INLINE
    size_type upper () const {
      return size_type();
    }

    // Storage accessors
    BOOST_UBLAS_INLINE
    const matrix_closure_type &data () const {
      return data_;
    }
    BOOST_UBLAS_INLINE
    matrix_closure_type &data () {
      return data_;
    }

    // Element access
#ifndef BOOST_UBLAS_PROXY_CONST_MEMBER
    BOOST_UBLAS_INLINE
    const_reference operator () (size_type i, size_type j) const {
      BOOST_UBLAS_CHECK (i < size1 (), bad_index ());
      BOOST_UBLAS_CHECK (j < size2 (), bad_index ());
#ifdef BOOST_UBLAS_OWN_BANDED
      if (i == j)
	return data () (i);
#else
      if (i == j)
	return data () (i);
#endif
      return zero_;
    }
    BOOST_UBLAS_INLINE
    reference operator () (size_type i, size_type j) {
      BOOST_UBLAS_CHECK (i < size1 (), bad_index ());
      BOOST_UBLAS_CHECK (j < size2 (), bad_index ());
#ifdef BOOST_UBLAS_OWN_BANDED
      if (i == j)
	return data () (i);
#else
      if (i == j)
	return data () (i);
#endif
#ifndef BOOST_UBLAS_REFERENCE_CONST_MEMBER
      bad_index ().raise ();
#endif
      return const_cast<reference>(zero_);
    }
#else
    BOOST_UBLAS_INLINE
    reference operator () (size_type i, size_type j) const {
      BOOST_UBLAS_CHECK (i < size1 (), bad_index ());
      BOOST_UBLAS_CHECK (j < size2 (), bad_index ());
#ifdef BOOST_UBLAS_OWN_BANDED
      if (i == j)
	return data () (i);
#else
      if (i == j)
	return data () (i);
#endif
#ifndef BOOST_UBLAS_REFERENCE_CONST_MEMBER
      bad_index ().raise ();
#endif
      return const_cast<reference>(zero_);
    }
#endif

    // Assignment
    BOOST_UBLAS_INLINE
    diagonal_vector_adaptor &operator = (const diagonal_vector_adaptor &m) {
      matrix_assign<scalar_assign> (*this, m);
      return *this;
    }
    BOOST_UBLAS_INLINE
    diagonal_vector_adaptor &assign_temporary (diagonal_vector_adaptor &m) {
      *this = m;
      return *this;
    }
    template<class AE>
    BOOST_UBLAS_INLINE
    diagonal_vector_adaptor &operator = (const matrix_expression<AE> &ae) {
      matrix_assign<scalar_assign> (*this, matrix<value_type> (ae));
      return *this;
    }
    template<class AE>
    BOOST_UBLAS_INLINE
    diagonal_vector_adaptor &assign (const matrix_expression<AE> &ae) {
      matrix_assign<scalar_assign> (*this, ae);
      return *this;
    }
    template<class AE>
    BOOST_UBLAS_INLINE
    diagonal_vector_adaptor& operator += (const matrix_expression<AE> &ae) {
      matrix_assign<scalar_assign> (*this, matrix<value_type> (*this + ae));
      return *this;
    }
    template<class AE>
    BOOST_UBLAS_INLINE
    diagonal_vector_adaptor &plus_assign (const matrix_expression<AE> &ae) {
      matrix_assign<scalar_plus_assign> (*this, ae);
      return *this;
    }
    template<class AE>
    BOOST_UBLAS_INLINE
    diagonal_vector_adaptor& operator -= (const matrix_expression<AE> &ae) {
      matrix_assign<scalar_assign> (*this, matrix<value_type> (*this - ae));
      return *this;
    }
    template<class AE>
    BOOST_UBLAS_INLINE
    diagonal_vector_adaptor &minus_assign (const matrix_expression<AE> &ae) {
      matrix_assign<scalar_minus_assign> (*this, ae);
      return *this;
    }
    template<class AT>
    BOOST_UBLAS_INLINE
    diagonal_vector_adaptor& operator *= (const AT &at) {
      matrix_assign_scalar<scalar_multiplies_assign> (*this, at);
      return *this;
    }
    template<class AT>
    BOOST_UBLAS_INLINE
    diagonal_vector_adaptor& operator /= (const AT &at) {
      matrix_assign_scalar<scalar_divides_assign> (*this, at);
      return *this;
    }

    // Closure comparison
    BOOST_UBLAS_INLINE
    bool same_closure (const diagonal_vector_adaptor &ba) const {
      return (*this).data ().same_closure (ba.data ());
    }

    // Swapping
    BOOST_UBLAS_INLINE
    void swap (diagonal_vector_adaptor &m) {
      if (this != &m) {
	BOOST_UBLAS_CHECK (lower_ == m.lower_, bad_size ());
	BOOST_UBLAS_CHECK (upper_ == m.upper_, bad_size ());
	matrix_swap<scalar_swap> (*this, m);
      }
    }
    BOOST_UBLAS_INLINE
    friend void swap (diagonal_vector_adaptor &m1, diagonal_vector_adaptor &m2) {
      m1.swap (m2);
    }

    // Iterator types
  private:
    // Use the matrix iterator
    typedef typename M::const_iterator const_subiterator1_type;
    typedef typename boost::mpl::if_<boost::is_const<M>,
				     typename M::const_iterator,
				     typename M::iterator>::type subiterator1_type;
    typedef typename M::const_iterator const_subiterator2_type;
    typedef typename boost::mpl::if_<boost::is_const<M>,
				     typename M::const_iterator,
				     typename M::iterator>::type subiterator2_type;

  public:
#ifdef BOOST_UBLAS_USE_INDEXED_ITERATOR
    typedef indexed_iterator1<self_type, packed_random_access_iterator_tag> iterator1;
    typedef indexed_iterator2<self_type, packed_random_access_iterator_tag> iterator2;
    typedef indexed_const_iterator1<self_type, packed_random_access_iterator_tag> const_iterator1;
    typedef indexed_const_iterator2<self_type, packed_random_access_iterator_tag> const_iterator2;
#else
    class const_iterator1;
    class iterator1;
    class const_iterator2;
    class iterator2;
#endif
    typedef reverse_iterator_base1<const_iterator1> const_reverse_iterator1;
    typedef reverse_iterator_base1<iterator1> reverse_iterator1;
    typedef reverse_iterator_base2<const_iterator2> const_reverse_iterator2;
    typedef reverse_iterator_base2<iterator2> reverse_iterator2;

    // Element lookup
    BOOST_UBLAS_INLINE
    const_iterator1 find1 (int rank, size_type i, size_type j) const {
      if (rank == 1) {
	size_type lower_i = (std::max) (difference_type (j - upper_), difference_type (0));
	i = (std::max) (i, lower_i);
	size_type upper_i = (std::min) (j + 1 + lower_, size1 ());
	i = (std::min) (i, upper_i);
      }
      return const_iterator1 (*this, data ().find (i));
    }
    BOOST_UBLAS_INLINE
    iterator1 find1 (int rank, size_type i, size_type j) {
      if (rank == 1) {
	size_type lower_i = (std::max) (difference_type (j - upper_), difference_type (0));
	i = (std::max) (i, lower_i);
	size_type upper_i = (std::min) (j + 1 + lower_, size1 ());
	i = (std::min) (i, upper_i);
      }
      return iterator1 (*this, data ().find (i));
    }
    BOOST_UBLAS_INLINE
    const_iterator2 find2 (int rank, size_type i, size_type j) const {
      if (rank == 1) {
	size_type lower_j = (std::max) (difference_type (i - lower_), difference_type (0));
	j = (std::max) (j, lower_j);
	size_type upper_j = (std::min) (i + 1 + upper_, size2 ());
	j = (std::min) (j, upper_j);
      }
      return const_iterator2 (*this, data ().find (j));
    }
    BOOST_UBLAS_INLINE
    iterator2 find2 (int rank, size_type i, size_type j) {
      if (rank == 1) {
	size_type lower_j = (std::max) (difference_type (i - lower_), difference_type (0));
	j = (std::max) (j, lower_j);
	size_type upper_j = (std::min) (i + 1 + upper_, size2 ());
	j = (std::min) (j, upper_j);
      }
      return iterator2 (*this, data ().find (j));
    }

    // Iterators simply are indices.

#ifndef BOOST_UBLAS_USE_INDEXED_ITERATOR
    class const_iterator1:
      public container_const_reference<diagonal_vector_adaptor>,
      public random_access_iterator_base<typename iterator_restrict_traits<
      typename const_subiterator1_type::iterator_category, packed_random_access_iterator_tag>::iterator_category,
      const_iterator1, value_type> {
    public:
      typedef typename const_subiterator1_type::value_type value_type;
      typedef typename const_subiterator1_type::difference_type difference_type;
      typedef typename const_subiterator1_type::reference reference;
      typedef typename const_subiterator1_type::pointer pointer;

      typedef const_iterator2 dual_iterator_type;
      typedef const_reverse_iterator2 dual_reverse_iterator_type;

      // Construction and destruction
      BOOST_UBLAS_INLINE
      const_iterator1 ():
	container_const_reference<self_type> (), it1_ () {}
      BOOST_UBLAS_INLINE
      const_iterator1 (const self_type &m, const const_subiterator1_type &it1):
	container_const_reference<self_type> (m), it1_ (it1) {}
      BOOST_UBLAS_INLINE
      const_iterator1 (const iterator1 &it):
	container_const_reference<self_type> (it ()), it1_ (it.it1_) {}

      // Arithmetic
      BOOST_UBLAS_INLINE
      const_iterator1 &operator ++ () {
	++ it1_;
	return *this;
      }
      BOOST_UBLAS_INLINE
      const_iterator1 &operator -- () {
	-- it1_;
	return *this;
      }
      BOOST_UBLAS_INLINE
      const_iterator1 &operator += (difference_type n) {
	it1_ += n;
	return *this;
      }
      BOOST_UBLAS_INLINE
      const_iterator1 &operator -= (difference_type n) {
	it1_ -= n;
	return *this;
      }
      BOOST_UBLAS_INLINE
      difference_type operator - (const const_iterator1 &it) const {
	BOOST_UBLAS_CHECK (&(*this) () == &it (), external_logic ());
	return it1_ - it.it1_;
      }

      // Dereference
      BOOST_UBLAS_INLINE
      const_reference operator * () const {
	size_type i = index1 ();
	size_type j = index2 ();
	BOOST_UBLAS_CHECK (i < (*this) ().size1 (), bad_index ());
	BOOST_UBLAS_CHECK (j < (*this) ().size2 (), bad_index ());
#ifdef BOOST_UBLAS_OWN_BANDED
	size_type k = (std::max) (i, j);
	size_type l = (*this) ().lower () + j - i;
	if (k < (std::max) ((*this) ().size1 (), (*this) ().size2 ()) &&
	    l < (*this) ().lower () + 1 + (*this) ().upper ())
	  return *it1_;
#else
	size_type k = j;
	size_type l = (*this) ().upper () + i - j;
	if (k < (*this) ().size2 () &&
	    l < (*this) ().lower () + 1 + (*this) ().upper ())
	  return *it1_;
#endif
	return (*this) () (i, j);
      }

#ifndef BOOST_UBLAS_NO_NESTED_CLASS_RELATION
      BOOST_UBLAS_INLINE
#ifdef BOOST_UBLAS_MSVC_NESTED_CLASS_RELATION
      typename self_type::
#endif
      const_iterator2 begin () const {
	return (*this) ().find2 (1, index1 (), 0);
      }
      BOOST_UBLAS_INLINE
#ifdef BOOST_UBLAS_MSVC_NESTED_CLASS_RELATION
      typename self_type::
#endif
      const_iterator2 end () const {
	return (*this) ().find2 (1, index1 (), (*this) ().size2 ());
      }
      BOOST_UBLAS_INLINE
#ifdef BOOST_UBLAS_MSVC_NESTED_CLASS_RELATION
      typename self_type::
#endif
      const_reverse_iterator2 rbegin () const {
	return const_reverse_iterator2 (end ());
      }
      BOOST_UBLAS_INLINE
#ifdef BOOST_UBLAS_MSVC_NESTED_CLASS_RELATION
      typename self_type::
#endif
      const_reverse_iterator2 rend () const {
	return const_reverse_iterator2 (begin ());
      }
#endif

      // Indices
      BOOST_UBLAS_INLINE
      size_type index1 () const {
	return it1_.index ();
      }
      BOOST_UBLAS_INLINE
      size_type index2 () const {
	return it1_.index ();
      }

      // Assignment
      BOOST_UBLAS_INLINE
      const_iterator1 &operator = (const const_iterator1 &it) {
	container_const_reference<self_type>::assign (&it ());
	it1_ = it.it1_;
	return *this;
      }

      // Comparison
      BOOST_UBLAS_INLINE
      bool operator == (const const_iterator1 &it) const {
	BOOST_UBLAS_CHECK (&(*this) () == &it (), external_logic ());
	return it1_ == it.it1_;
      }
      BOOST_UBLAS_INLINE
      bool operator < (const const_iterator1 &it) const {
	BOOST_UBLAS_CHECK (&(*this) () == &it (), external_logic ());
	return it1_ < it.it1_;
      }

    private:
      const_subiterator1_type it1_;
    };
#endif

    BOOST_UBLAS_INLINE
    const_iterator1 begin1 () const {
      return find1 (0, 0, 0);
    }
    BOOST_UBLAS_INLINE
    const_iterator1 end1 () const {
      return find1 (0, size1 (), 0);
    }

#ifndef BOOST_UBLAS_USE_INDEXED_ITERATOR
    class iterator1:
      public container_reference<diagonal_vector_adaptor>,
      public random_access_iterator_base<typename iterator_restrict_traits<
      typename subiterator1_type::iterator_category, packed_random_access_iterator_tag>::iterator_category,
      iterator1, value_type> {
    public:
      typedef typename subiterator1_type::value_type value_type;
      typedef typename subiterator1_type::difference_type difference_type;
      typedef typename subiterator1_type::reference reference;
      typedef typename subiterator1_type::pointer pointer;

      typedef iterator2 dual_iterator_type;
      typedef reverse_iterator2 dual_reverse_iterator_type;

      // Construction and destruction
      BOOST_UBLAS_INLINE
      iterator1 ():
	container_reference<self_type> (), it1_ () {}
      BOOST_UBLAS_INLINE
      iterator1 (self_type &m, const subiterator1_type &it1):
	container_reference<self_type> (m), it1_ (it1) {}

      // Arithmetic
      BOOST_UBLAS_INLINE
      iterator1 &operator ++ () {
	++ it1_;
	return *this;
      }
      BOOST_UBLAS_INLINE
      iterator1 &operator -- () {
	-- it1_;
	return *this;
      }
      BOOST_UBLAS_INLINE
      iterator1 &operator += (difference_type n) {
	it1_ += n;
	return *this;
      }
      BOOST_UBLAS_INLINE
      iterator1 &operator -= (difference_type n) {
	it1_ -= n;
	return *this;
      }
      BOOST_UBLAS_INLINE
      difference_type operator - (const iterator1 &it) const {
	BOOST_UBLAS_CHECK (&(*this) () == &it (), external_logic ());
	return it1_ - it.it1_;
      }

      // Dereference
      BOOST_UBLAS_INLINE
      reference operator * () const {
	size_type i = index1 ();
	size_type j = index2 ();
	BOOST_UBLAS_CHECK (i < (*this) ().size1 (), bad_index ());
	BOOST_UBLAS_CHECK (j < (*this) ().size2 (), bad_index ());
#ifdef BOOST_UBLAS_OWN_BANDED
	size_type k = (std::max) (i, j);
	size_type l = (*this) ().lower () + j - i;
	if (k < (std::max) ((*this) ().size1 (), (*this) ().size2 ()) &&
	    l < (*this) ().lower () + 1 + (*this) ().upper ())
	  return *it1_;
#else
	size_type k = j;
	size_type l = (*this) ().upper () + i - j;
	if (k < (*this) ().size2 () &&
	    l < (*this) ().lower () + 1 + (*this) ().upper ())
	  return *it1_;
#endif
	return (*this) () (i, j);
      }

#ifndef BOOST_UBLAS_NO_NESTED_CLASS_RELATION
      BOOST_UBLAS_INLINE
#ifdef BOOST_UBLAS_MSVC_NESTED_CLASS_RELATION
      typename self_type::
#endif
      iterator2 begin () const {
	return (*this) ().find2 (1, index1 (), 0);
      }
      BOOST_UBLAS_INLINE
#ifdef BOOST_UBLAS_MSVC_NESTED_CLASS_RELATION
      typename self_type::
#endif
      iterator2 end () const {
	return (*this) ().find2 (1, index1 (), (*this) ().size2 ());
      }
      BOOST_UBLAS_INLINE
#ifdef BOOST_UBLAS_MSVC_NESTED_CLASS_RELATION
      typename self_type::
#endif
      reverse_iterator2 rbegin () const {
	return reverse_iterator2 (end ());
      }
      BOOST_UBLAS_INLINE
#ifdef BOOST_UBLAS_MSVC_NESTED_CLASS_RELATION
      typename self_type::
#endif
      reverse_iterator2 rend () const {
	return reverse_iterator2 (begin ());
      }
#endif

      // Indices
      BOOST_UBLAS_INLINE
      size_type index1 () const {
	return it1_.index1 ();
      }
      BOOST_UBLAS_INLINE
      size_type index2 () const {
	return it1_.index2 ();
      }

      // Assignment
      BOOST_UBLAS_INLINE
      iterator1 &operator = (const iterator1 &it) {
	container_reference<self_type>::assign (&it ());
	it1_ = it.it1_;
	return *this;
      }

      // Comparison
      BOOST_UBLAS_INLINE
      bool operator == (const iterator1 &it) const {
	BOOST_UBLAS_CHECK (&(*this) () == &it (), external_logic ());
	return it1_ == it.it1_;
      }
      BOOST_UBLAS_INLINE
      bool operator < (const iterator1 &it) const {
	BOOST_UBLAS_CHECK (&(*this) () == &it (), external_logic ());
	return it1_ < it.it1_;
      }

    private:
      subiterator1_type it1_;

      friend class const_iterator1;
    };
#endif

    BOOST_UBLAS_INLINE
    iterator1 begin1 () {
      return find1 (0, 0, 0);
    }
    BOOST_UBLAS_INLINE
    iterator1 end1 () {
      return find1 (0, size1 (), 0);
    }

#ifndef BOOST_UBLAS_USE_INDEXED_ITERATOR
    class const_iterator2:
      public container_const_reference<diagonal_vector_adaptor>,
      public random_access_iterator_base<packed_random_access_iterator_tag,
      const_iterator2, value_type> {
    public:
      typedef typename iterator_restrict_traits<typename const_subiterator2_type::iterator_category,
						packed_random_access_iterator_tag>::iterator_category iterator_category;
      typedef typename const_subiterator2_type::value_type value_type;
      typedef typename const_subiterator2_type::difference_type difference_type;
      typedef typename const_subiterator2_type::reference reference;
      typedef typename const_subiterator2_type::pointer pointer;

      typedef const_iterator1 dual_iterator_type;
      typedef const_reverse_iterator1 dual_reverse_iterator_type;

      // Construction and destruction
      BOOST_UBLAS_INLINE
      const_iterator2 ():
	container_const_reference<self_type> (), it2_ () {}
      BOOST_UBLAS_INLINE
      const_iterator2 (const self_type &m, const const_subiterator2_type &it2):
	container_const_reference<self_type> (m), it2_ (it2) {}
      BOOST_UBLAS_INLINE
      const_iterator2 (const iterator2 &it):
	container_const_reference<self_type> (it ()), it2_ (it.it2_) {}

      // Arithmetic
      BOOST_UBLAS_INLINE
      const_iterator2 &operator ++ () {
	++ it2_;
	return *this;
      }
      BOOST_UBLAS_INLINE
      const_iterator2 &operator -- () {
	-- it2_;
	return *this;
      }
      BOOST_UBLAS_INLINE
      const_iterator2 &operator += (difference_type n) {
	it2_ += n;
	return *this;
      }
      BOOST_UBLAS_INLINE
      const_iterator2 &operator -= (difference_type n) {
	it2_ -= n;
	return *this;
      }
      BOOST_UBLAS_INLINE
      difference_type operator - (const const_iterator2 &it) const {
	BOOST_UBLAS_CHECK (&(*this) () == &it (), external_logic ());
	return it2_ - it.it2_;
      }

      // Dereference
      BOOST_UBLAS_INLINE
      const_reference operator * () const {
	size_type i = index1 ();
	size_type j = index2 ();
	BOOST_UBLAS_CHECK (i < (*this) ().size1 (), bad_index ());
	BOOST_UBLAS_CHECK (j < (*this) ().size2 (), bad_index ());
#ifdef BOOST_UBLAS_OWN_BANDED
	size_type k = (std::max) (i, j);
	size_type l = (*this) ().lower () + j - i;
	if (k < (std::max) ((*this) ().size1 (), (*this) ().size2 ()) &&
	    l < (*this) ().lower () + 1 + (*this) ().upper ())
	  return *it2_;
#else
	size_type k = j;
	size_type l = (*this) ().upper () + i - j;
	if (k < (*this) ().size2 () &&
	    l < (*this) ().lower () + 1 + (*this) ().upper ())
	  return *it2_;
#endif
	return (*this) () (i, j);
      }

#ifndef BOOST_UBLAS_NO_NESTED_CLASS_RELATION
      BOOST_UBLAS_INLINE
#ifdef BOOST_UBLAS_MSVC_NESTED_CLASS_RELATION
      typename self_type::
#endif
      const_iterator1 begin () const {
	return (*this) ().find1 (1, 0, index2 ());
      }
      BOOST_UBLAS_INLINE
#ifdef BOOST_UBLAS_MSVC_NESTED_CLASS_RELATION
      typename self_type::
#endif
      const_iterator1 end () const {
	return (*this) ().find1 (1, (*this) ().size1 (), index2 ());
      }
      BOOST_UBLAS_INLINE
#ifdef BOOST_UBLAS_MSVC_NESTED_CLASS_RELATION
      typename self_type::
#endif
      const_reverse_iterator1 rbegin () const {
	return const_reverse_iterator1 (end ());
      }
      BOOST_UBLAS_INLINE
#ifdef BOOST_UBLAS_MSVC_NESTED_CLASS_RELATION
      typename self_type::
#endif
      const_reverse_iterator1 rend () const {
	return const_reverse_iterator1 (begin ());
      }
#endif

      // Indices
      BOOST_UBLAS_INLINE
      size_type index1 () const {
	return it2_.index ();
      }
      BOOST_UBLAS_INLINE
      size_type index2 () const {
	return it2_.index ();
      }

      // Assignment
      BOOST_UBLAS_INLINE
      const_iterator2 &operator = (const const_iterator2 &it) {
	container_const_reference<self_type>::assign (&it ());
	it2_ = it.it2_;
	return *this;
      }

      // Comparison
      BOOST_UBLAS_INLINE
      bool operator == (const const_iterator2 &it) const {
	BOOST_UBLAS_CHECK (&(*this) () == &it (), external_logic ());
	return it2_ == it.it2_;
      }
      BOOST_UBLAS_INLINE
      bool operator < (const const_iterator2 &it) const {
	BOOST_UBLAS_CHECK (&(*this) () == &it (), external_logic ());
	return it2_ < it.it2_;
      }

    private:
      const_subiterator2_type it2_;
    };
#endif

    BOOST_UBLAS_INLINE
    const_iterator2 begin2 () const {
      return find2 (0, 0, 0);
    }
    BOOST_UBLAS_INLINE
    const_iterator2 end2 () const {
      return find2 (0, 0, size2 ());
    }

#ifndef BOOST_UBLAS_USE_INDEXED_ITERATOR
    class iterator2:
      public container_reference<diagonal_vector_adaptor>,
      public random_access_iterator_base<typename iterator_restrict_traits<
      typename subiterator2_type::iterator_category, packed_random_access_iterator_tag>::iterator_category,
      iterator2, value_type> {
    public:
      typedef typename subiterator2_type::value_type value_type;
      typedef typename subiterator2_type::difference_type difference_type;
      typedef typename subiterator2_type::reference reference;
      typedef typename subiterator2_type::pointer pointer;

      typedef iterator1 dual_iterator_type;
      typedef reverse_iterator1 dual_reverse_iterator_type;

      // Construction and destruction
      BOOST_UBLAS_INLINE
      iterator2 ():
	container_reference<self_type> (), it2_ () {}
      BOOST_UBLAS_INLINE
      iterator2 (self_type &m, const subiterator2_type &it2):
	container_reference<self_type> (m), it2_ (it2) {}

      // Arithmetic
      BOOST_UBLAS_INLINE
      iterator2 &operator ++ () {
	++ it2_;
	return *this;
      }
      BOOST_UBLAS_INLINE
      iterator2 &operator -- () {
	-- it2_;
	return *this;
      }
      BOOST_UBLAS_INLINE
      iterator2 &operator += (difference_type n) {
	it2_ += n;
	return *this;
      }
      BOOST_UBLAS_INLINE
      iterator2 &operator -= (difference_type n) {
	it2_ -= n;
	return *this;
      }
      BOOST_UBLAS_INLINE
      difference_type operator - (const iterator2 &it) const {
	BOOST_UBLAS_CHECK (&(*this) () == &it (), external_logic ());
	return it2_ - it.it2_;
      }

      // Dereference
      BOOST_UBLAS_INLINE
      reference operator * () const {
	size_type i = index1 ();
	size_type j = index2 ();
	BOOST_UBLAS_CHECK (i < (*this) ().size1 (), bad_index ());
	BOOST_UBLAS_CHECK (j < (*this) ().size2 (), bad_index ());
#ifdef BOOST_UBLAS_OWN_BANDED
	size_type k = (std::max) (i, j);
	size_type l = (*this) ().lower () + j - i;
	if (k < (std::max) ((*this) ().size1 (), (*this) ().size2 ()) &&
	    l < (*this) ().lower () + 1 + (*this) ().upper ())
	  return *it2_;
#else
	size_type k = j;
	size_type l = (*this) ().upper () + i - j;
	if (k < (*this) ().size2 () &&
	    l < (*this) ().lower () + 1 + (*this) ().upper ())
	  return *it2_;
#endif
	return (*this) () (i, j);
      }

#ifndef BOOST_UBLAS_NO_NESTED_CLASS_RELATION
      BOOST_UBLAS_INLINE
#ifdef BOOST_UBLAS_MSVC_NESTED_CLASS_RELATION
      typename self_type::
#endif
      iterator1 begin () const {
	return (*this) ().find1 (1, 0, index2 ());
      }
      BOOST_UBLAS_INLINE
#ifdef BOOST_UBLAS_MSVC_NESTED_CLASS_RELATION
      typename self_type::
#endif
      iterator1 end () const {
	return (*this) ().find1 (1, (*this) ().size1 (), index2 ());
      }
      BOOST_UBLAS_INLINE
#ifdef BOOST_UBLAS_MSVC_NESTED_CLASS_RELATION
      typename self_type::
#endif
      reverse_iterator1 rbegin () const {
	return reverse_iterator1 (end ());
      }
      BOOST_UBLAS_INLINE
#ifdef BOOST_UBLAS_MSVC_NESTED_CLASS_RELATION
      typename self_type::
#endif
      reverse_iterator1 rend () const {
	return reverse_iterator1 (begin ());
      }
#endif

      // Indices
      BOOST_UBLAS_INLINE
      size_type index1 () const {
	return it2_.index1 ();
      }
      BOOST_UBLAS_INLINE
      size_type index2 () const {
	return it2_.index2 ();
      }

      // Assignment
      BOOST_UBLAS_INLINE
      iterator2 &operator = (const iterator2 &it) {
	container_reference<self_type>::assign (&it ());
	it2_ = it.it2_;
	return *this;
      }

      // Comparison
      BOOST_UBLAS_INLINE
      bool operator == (const iterator2 &it) const {
	BOOST_UBLAS_CHECK (&(*this) () == &it (), external_logic ());
	return it2_ == it.it2_;
      }
      BOOST_UBLAS_INLINE
      bool operator < (const iterator2 &it) const {
	BOOST_UBLAS_CHECK (&(*this) () == &it (), external_logic ());
	return it2_ < it.it2_;
      }

    private:
      subiterator2_type it2_;

      friend class const_iterator2;
    };
#endif

    BOOST_UBLAS_INLINE
    iterator2 begin2 () {
      return find2 (0, 0, 0);
    }
    BOOST_UBLAS_INLINE
    iterator2 end2 () {
      return find2 (0, 0, size2 ());
    }

    // Reverse iterators

    BOOST_UBLAS_INLINE
    const_reverse_iterator1 rbegin1 () const {
      return const_reverse_iterator1 (end1 ());
    }
    BOOST_UBLAS_INLINE
    const_reverse_iterator1 rend1 () const {
      return const_reverse_iterator1 (begin1 ());
    }

    BOOST_UBLAS_INLINE
    reverse_iterator1 rbegin1 () {
      return reverse_iterator1 (end1 ());
    }
    BOOST_UBLAS_INLINE
    reverse_iterator1 rend1 () {
      return reverse_iterator1 (begin1 ());
    }

    BOOST_UBLAS_INLINE
    const_reverse_iterator2 rbegin2 () const {
      return const_reverse_iterator2 (end2 ());
    }
    BOOST_UBLAS_INLINE
    const_reverse_iterator2 rend2 () const {
      return const_reverse_iterator2 (begin2 ());
    }

    BOOST_UBLAS_INLINE
    reverse_iterator2 rbegin2 () {
      return reverse_iterator2 (end2 ());
    }
    BOOST_UBLAS_INLINE
    reverse_iterator2 rend2 () {
      return reverse_iterator2 (begin2 ());
    }

  private:
    matrix_closure_type data_;
    size_type lower_;
    size_type upper_;
    typedef const value_type const_value_type;
    static const_value_type zero_;
  };

  template<class M>
  typename diagonal_vector_adaptor<M>::const_value_type diagonal_vector_adaptor<M>::zero_ = value_type/*zero*/();

    
  template<class M>
  BOOST_UBLAS_INLINE
  matrix_vector_slice<M> diag(M &data) {
    const typename M::size_type s = std::min(data.size1(),data.size2());
    return matrix_vector_slice<M>(data, slice(0,1,s), slice(0,1,s));
  }

  template<class M>
  BOOST_UBLAS_INLINE
  const matrix_vector_slice<const M> diag(const M &data) {
    const typename M::size_type s = std::min(data.size1(),data.size2());
    return matrix_vector_slice<const M>(data, slice(0,1,s), slice(0,1,s));
  }

  template<class V>
  BOOST_UBLAS_INLINE
  diagonal_vector_adaptor<V> diagm(V& data) {
    return diagonal_vector_adaptor<V>(data);
  }

  template<class V>
  BOOST_UBLAS_INLINE
  const diagonal_vector_adaptor<const V> diagm(const V& data) {
    return diagonal_vector_adaptor<const V>(data);
  }


}}}

#endif
