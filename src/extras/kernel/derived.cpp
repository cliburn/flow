#include <boost/shared_ptr.hpp>
#include <iostream>
using std::cout;
using std::endl;
using boost::shared_ptr;

class Base
{
public:
  virtual int f() {
    return 1;
  }
};

class Derived : public Base
{
public:
  int f() {
    return 2;
  }
};

int main()
{
  boost::shared_ptr<Base> dp(new Derived);
  boost::shared_ptr<Base> bp(new Base);
  cout << bp->f() << endl;
  cout << dp->f() << endl;
}
