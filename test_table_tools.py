import unittest
from table_tools import Table, TableGrouped

class testTable(unittest.TestCase):

    def setUp(self):
        self.t1 = Table({'a': [1, 2, 3], 'b': [3, 2, 1]})
        self.t2 = Table({'x': ['a', 'b'], 'y': ['b', 'a']})
        self.t3 = Table({
            'a': [0, 0, 2, 2, 1, 1],
            'b': [1, 2, 1, 2, 1, 2],
            'c': [2, 1, 2, 1, 2, 1]
        })
        self.t4 = Table({
            'a': [0, 0, 0, 1, 2, 2],
            'b': [1, 2, 1, 2, 1, 2],
            'c': [2, 1, 2, 1, 2, 1]
        })

    def test_field_names(self):
        self.assertEquals(set(self.t1.field_names()), set(['a', 'b']))
        self.assertEquals(set(self.t2.field_names()), set(['x', 'y']))

    def test_get_column(self):
        self.assertEquals(self.t1['a'], [1, 2, 3])
        self.assertEquals(self.t1['b'], [3, 2, 1])

    def test_add_field(self):
        t = Table({'a': [1, 2, 3], 'b': [3, 2, 1]})
        with self.assertRaises(ValueError):
            t.add_field('c', [0, 0])
        t.add_field('c', [0, 0, 0])
        self.assertEqual(t['c'], [0, 0, 0])

    def test_get_row(self):
        self.assertEquals(self.t1[0], {'a': 1, 'b': 3})
        self.assertEquals(self.t1[1], {'a': 2, 'b': 2})
        self.assertEquals(self.t1[2], {'a': 3, 'b': 1})

    def test_get_slice(self):
        self.assertEquals(self.t1[0:], Table({'a': [1, 2, 3], 'b': [3, 2, 1]}))
        self.assertEquals(self.t1[1:], Table({'a': [2, 3], 'b': [2, 1]}))
        self.assertEquals(self.t1[:2], Table({'a': [1, 2], 'b': [3, 2]}))

    def test_map_across_field(self):
        self.assertEquals(self.t1.map_across_field('a', lambda x: 2*x),
                          [2, 4, 6])
        self.assertEquals(self.t1.map_across_field('b', lambda x: 2*x),
                          [6, 4, 2])
        self.assertEquals(self.t1.map_across_field('a', lambda x: 0),
                          [0, 0, 0])

    def test_map(self):
        self.assertEquals(self.t1.map(lambda a, b: a*b), [3, 4, 3])
        self.assertEquals(self.t2.map(lambda x, y: x + y), ['ab', 'ba'])

    def test_sort_single_field(self):
        self.assertEquals(self.t1.sort('a'), self.t1)
        self.assertEquals(self.t1.sort('b'), 
                          Table({'a': [3, 2, 1], 'b': [1, 2, 3]}))
        self.assertEquals(self.t2.sort('x'), self.t2)
        self.assertEquals(self.t2.sort('y'),
                          Table({'x': ['b', 'a'], 'y': ['a', 'b']}))

    def test_sort_two_fields(self):
        self.assertEquals(
            self.t3.sort('a', 'b'),
            Table({
                'a': [0, 0, 1, 1, 2, 2],
                'b': [1, 2, 1, 2, 1, 2],
                'c': [2, 1, 2, 1, 2, 1]
            })
        )
        self.assertEquals(
            self.t3.sort('b', 'a'),
            Table({
                'a': [0, 1, 2, 0, 1, 2],
                'b': [1, 1, 1, 2, 2, 2],
                'c': [2, 2, 2, 1, 1, 1]
            })
        )

    def test_groupby(self):
        self.assertEquals(
            self.t3.groupby('a'),
            TableGrouped(
                [
                    Table({'a': [0 ,0], 'b': [1, 2], 'c': [2, 1]}),
                    Table({'a': [2, 2], 'b': [1, 2], 'c': [2, 1]}),
                    Table({'a': [1, 1], 'b': [1, 2], 'c': [2, 1]})
                ]
            )
        )
        self.assertEquals(
            self.t3.sort('b').groupby('b'),
            TableGrouped(
                [
                    Table({'a': [0, 2, 1], 'b': [1, 1, 1], 'c': [2, 2, 2]}),
                    Table({'a': [0, 2, 1], 'b': [2, 2, 2], 'c': [1, 1, 1]})
                ]
            )
        )
                    
    def test_reduce(self):
        self.assertEquals(
            self.t3.groupby('a').reduce(lambda x: min(x['b'])),
            [1, 1, 1, 1, 1, 1]
        )
        self.assertEquals(
            self.t3.groupby('a').reduce(lambda x: min(x['b'])),
            [1, 1, 1, 1, 1, 1]
        )
        self.assertEquals(
            self.t4.groupby('a').reduce(lambda x: sum(x['b'])),
            [4, 4, 4, 2, 3, 3]
        )
