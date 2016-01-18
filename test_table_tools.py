import unittest

from table_tools import Table

class testTable(unittest.TestCase):

    def setUp(self):
        self.t1 = Table({'a': [1, 2, 3], 'b': [3, 2, 1]})

    def test_get_column(self):
        self.assertEquals(self.t1['a'], [1, 2, 3])
        self.assertEquals(self.t1['b'], [3, 2, 1])

    def test_get_row(self):
        self.assertEquals(self.t1[0], {'a': 1, 'b': 3})
        self.assertEquals(self.t1[1], {'a': 2, 'b': 2})
        self.assertEquals(self.t1[2], {'a': 3, 'b': 1})

    def test_get_slice(self):
        self.assertEquals(self.t1[0:], {'a': [1, 2, 3], 'b': [3, 2, 1]})
        self.assertEquals(self.t1[1:], {'a': [2, 3], 'b': [2, 1]})
        self.assertEquals(self.t1[:2], {'a': [1, 2], 'b': [3, 2]})
