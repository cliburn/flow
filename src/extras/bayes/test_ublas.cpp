#include <boost/numeric/ublas/matrix.hpp>
#include <boost/numeric/ublas/io.hpp>
using std::cout;

namespace ublas = boost::numeric::ublas;

int main() {
  ublas::matrix<double> A(3, 3);
  for (int i=0; i<3; ++i)
    for (int j=0; j<3; ++j)
      A(i,j) = i*3+j;

  cout << A << "\n";
}
