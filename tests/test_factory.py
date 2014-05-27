"""Test creation of a function from a string."""

import sys
sys.path.append('../src')
import factory
import unittest

def double(x):
    return x*2

class TestFactory(unittest.TestCase):
    def test_double(self):
        args = ['double', 2]
        self.assertEqual(factory.factory('__main__', args[0], *args[1:]), 4)

    def test_log(self):
        x1 = factory.factory('numpy', 'log', 10.0)
        import numpy
        x2 = numpy.log(10.0)
        self.assertEqual(x1, x2)

    def test_double2(self):
        args = ['double', 2]
        f = factory.forname('__main__', args[0])
        self.assertEqual(f(*args[1:]), 4)        

if __name__ == '__main__':
    unittest.main()
