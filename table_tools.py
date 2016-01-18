from pprint import pformat
from operator import itemgetter


def _check_lengths(d):
    check_len = len(d[d.keys()[0]])
    return all(len(val) == check_len for val in d.itervalues())

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

    def field_names(self):
        return set(self._data.keys())

    def add_field(self, field_name, vector):
        if not len(vector) == self._n_row:
            raise ValueError("Length of vector must be equal to number of rows"
                             " in table.")
        self._data[field_name] = vector

    def __repr__(self):
        return pformat(self._data)

    def __getitem__(self, idxr):
        if isinstance(idxr, basestring):
            return self._getitem_string(idxr)
        elif isinstance(idxr, (int, long, slice)):
            return self._getitem_int_or_slice(idxr)
        else:
            raise ValueError("Unknown type supplied to __getitem__")

    def _getitem_string(self, key):
        return self._data[key]

    def _getitem_int_or_slice(self, idxr):
        return {
            field_name: self[field_name][idxr]
            for field_name in self.field_names()
        }

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

    def sort_by_field(self, field_name):
        field_names, matrix = self._to_matrix()
        col_idx = field_names.index(field_name)
        sorted_matrix = sorted(matrix, key=itemgetter(col_idx))
        return Table.from_matrix(field_names, sorted_matrix)

    def _to_matrix(self):
        field_names = self.field_names()
        matrix = [
            [self[key][i] for key in self.field_names()]
            for i in range(self._n_row)
        ]
        return field_names, matrix

    def groupby(self, field, mapper=None):
        if mapper == None:
            mapper = lambda x: x
        pass


class TableGrouped(object):
   pass
