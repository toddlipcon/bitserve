#!/usr/bin/env python
#
# Represents a table with several columns

from column import Column
import unittest

class Table:
    def __init__(self):
        self.columns = {}
        self.num_rows = 0


    def append_row(self, data):
        """Appends a row. data should be a dictionary
        whose keys are column names and values are either
        single values or sets"""

        new_row_count = self.num_rows + 1
        for (col, val) in data.iteritems():
            if col not in self.columns:
                self.columns[col] = Column(self.num_rows)
            col_row_count = self.columns[col].append(val)
            assert col_row_count == new_row_count

        self.num_rows = new_row_count
        return new_row_count

    def query(self, q):
        bs = q.resolve_to_bitset(self)
        # TODO: convert to list
        return bs

    def get_column(self, name):
        return self.columns[name]


class JunctionQuery:
    """A query that wraps two subqueries with a bitwise op"""
    OP_AND = 'AND'
    OP_OR  = 'OR'

    def __init__(self, left, right, operator):
        self.left = left
        self.right = right
        self.op = operator

    def resolve_to_bitset(self, table):
        bs_left = self.left.resolve_to_bitset(table)
        bs_right = self.right.resolve_to_bitset(table)
        
        if self.op == self.OP_AND:
            return bs_left & bs_right
        elif self.op == self.OP_OR:
            return bs_left | bs_right
        else:
            raise Exception("unknown op: " + self.op)
    
def MultiJunctionQuery(queries, operator):
    assert len(queries) > 0
    if len(queries) == 1:
        return queries[0]
    left = queries[0]
    for q in queries[1:]:
        left = JunctionQuery(left, q, operator)

    return left
    


class ColumnQuery:
    """A query that specifies an equality or range condition on a column."""

    TYPE_EQ = '='
    TYPE_LTE = '<='
    TYPE_GTE = '>='
    
    def __init__(self, colname, param, type = TYPE_EQ):
        self.colname = colname
        self.type = type
        self.param = param

    def resolve_to_bitset(self, table):
        col = table.get_column(self.colname)
        
        if self.type == self.TYPE_EQ:
            return col.get_index(self.param)
        elif self.type == self.TYPE_LTE:
            return col.get_range_index(None, self.param)
        elif self.type == self.TYPE_GTE:
            return col.get_range_index(self.param, None)


class TableTestCase(unittest.TestCase):
    def setUp(self):
        t = Table()
        t.append_row({'price': 98,
                      'territories': set(['us','ca']),
                      'genres': set(['rock','pop','powerpop'])})
        t.append_row({'price': 45,
                      'territories': set(['us','gb']),
                      'genres': set(['rock','pop','powerpop'])})
        t.append_row({'price': 0,
                      'territories': set(['us','ca']),
                      'genres': set(['emo','powerpop'])})
        t.append_row({'price': 0,
                      'territories': set(['us','ca','gb']),
                      'genres': set(['rock','blues','jazz'])})
        self.t = t

    def testNumRows(self):
        self.assertEqual(self.t.num_rows, 4)

    def testColumnQuery(self):
        q = ColumnQuery("genres", "rock")
        self.assertEqual(str(self.t.query(q)), "1101")

        q = ColumnQuery("price", 1, ColumnQuery.TYPE_GTE)
        self.assertEqual(str(self.t.query(q)), "1100")

        q = ColumnQuery("price", 1, ColumnQuery.TYPE_LTE)
        self.assertEqual(str(self.t.query(q)), "0011")

    def testJunctionQuery(self):
        # rock and pop
        q = JunctionQuery(
            ColumnQuery("genres", "rock"),
            ColumnQuery("genres", "pop"),
            JunctionQuery.OP_AND)
        self.assertEqual(str(self.t.query(q)),
                         "1100")

        # rock or pop
        q = JunctionQuery(
            ColumnQuery("genres", "rock"),
            ColumnQuery("genres", "pop"),
            JunctionQuery.OP_OR)
        self.assertEqual(str(self.t.query(q)),
                         "1101")


if __name__ == '__main__':
    unittest.main(defaultTest = "TableTestCase")

