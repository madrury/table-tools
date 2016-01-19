from pprint import pformat
from operator import itemgetter
from itertools import groupby

# I want to support things like this
#
# t.sort('x', 'y').groupby('x').first()
# t.sort('x', 'y').groupby('x').lag(1).first()

def _check_lengths(d):
    check_len = len(d[d.keys()[0]])
    return all(len(val) == check_len for val in d.itervalues())

def _accumulate(iterable):
    total = 0
    for e in iterable:
        total += e
        yield total

def _get_transition_slices(lst):
    group_lengths = (len(list(grp)) for elem, grp in groupby(lst))
    slice_ends = list(_accumulate(group_lengths))
    slice_begins = [0] + slice_ends[:-1]
    return [slice(i, j) for i, j in zip(slice_begins, slice_ends)]
    

class Table(object):

    def __init__(self, d):
        if not _check_lengths(d):
            raise ValueError("All lists in inital dictionary must have the same"
                            " length.")
        self._data = d
        self._n_row = len(d[d.keys()[0]])

    @classmethod
    def from_matrix(cls, field_names, matrix):
        if not matrix:
            raise ValueError("array_of_tupes must not be empty.")
        n_col = len(matrix[0])
        if not all(len(row) == n_col  for row in matrix):
            raise ValueError("Each row in array_of_tupes must have the same"
                             " length.")
        if len(field_names) != n_col:
            raise ValueError("Field_names must have same length as"
                             " the number of columns")
        n_row = len(matrix)
        d = {key: [matrix[i][j] for i in range(n_row)]
             for j, key in enumerate(field_names)
        }
        return cls(d)

    def __eq__(self, other):
        return self._data == other._data

    def field_names(self):
        return self._data.keys()

    def add_field(self, field_name, vector):
        if not len(vector) == self._n_row:
            raise ValueError("Length of vector must be equal to number of rows"
                             " in table.")
        self._data[field_name] = vector

    def __repr__(self):
        return  'Table(' + pformat(self._data) + ')'

    def __getitem__(self, idxr):
        if isinstance(idxr, basestring):
            return self._getitem_string(idxr)
        elif isinstance(idxr, (int, long)):
            return self._getitem_int(idxr)
        elif isinstance(idxr, slice):
            return self._getitem_slice(idxr)
        else:
            raise ValueError("Unknown type supplied to __getitem__")

    def _getitem_string(self, key):
        return self._data[key]

    def _getitem_int(self, idxr):
        return {
            field_name: self[field_name][idxr]
            for field_name in self.field_names()
        }

    def _getitem_slice(self, idxr):
        return Table({
            field_name: self[field_name][idxr]
            for field_name in self.field_names()
        })

    def __iter__(self):
        for i in range(self._n_row):
            yield self[i]

    def map_across_field(self, field_name, f):
        return [f(x) for x in self[field_name]]

    def map(self, f):
        return list(self._iter_map(f))

    def _iter_map(self, f):
        for row in self:
            yield(f(**row))

    def sort(self, *orderands):
        field_names, matrix = self._to_matrix()
        col_idxs = [field_names.index(f) for f in orderands]
        sorted_matrix = sorted(matrix, key=itemgetter(*col_idxs))
        return Table.from_matrix(field_names, sorted_matrix)

    def _to_matrix(self):
        field_names = self.field_names()
        matrix = [
            [self[key][i] for key in self.field_names()]
            for i in range(self._n_row)
        ]
        return field_names, matrix

    def groupby(self, field_name):
        field = self[field_name]
        slices = _get_transition_slices(field)
        tables = []
        for sl in slices:
            tables.append(self[sl])
        return TableGrouped(tables)
        

class TableGrouped(object):

    def __init__(self, array_of_tables):
        self._data = array_of_tables
        self._grp_lens = [x._n_row for x in array_of_tables]
        self._offset = 0

    def __repr__(self):
        return self._data.__repr__()

    def __eq__(self, other):
        return self._data == other._data

    def __iter__(self):
        for table in self._data:
            yield table

    def __getitem__(self, idx):
        return self._data[idx]

    def lag(self, n):
        if n < 0:
            raise ValueError("Lag must be non-negative.")
        self._offset = n
        return self

    def reduce(self, f, default=''):
        reduced = []
        for i, x in enumerate(self):
            if i < self._offset:
                reduced.extend([default] * x._n_row)
            else:
                reduced.extend([f(self[i - self._offset])] * x._n_row)
        return reduced

    def first(self, field_name, default=''):
        return self.reduce(lambda x: x[field_name][0], default=default)

    def last(self, field_name, default=''):
        return self.reduce(lambda x: x[field_name][-1], default=default)

    def min(self, field_name, default=''):
        return self.reduce(lambda x: min(x[field_name]), default=default)

    def max(self, field_name, default=''):
        return self.reduce(lambda x: min(x[field_name]), default=default)
