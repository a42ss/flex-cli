import unittest
from ... import lcli
from lcli import *

class TestStringMethods(unittest.TestCase):

    def test_module_variables(self):
        self.assertTrue(hasattr(lcli, '__version__'))


if __name__ == '__main__':
    unittest.main()
