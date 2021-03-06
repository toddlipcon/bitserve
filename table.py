#!/usr/bin/env python
#
# Represents a table with several columns

from column import Column
import unittest

class Table:
    def __init__(self):
        self.columns = {}
        self.num_rows = 0
        self.row_to_id = {}


    def append_row(self, id, data):
        """Appends a row. data should be a dictionary
        whose keys are column names and values are either
        single values or sets"""

        new_row_count = self.num_rows + 1
        for (col, val) in data.iteritems():
            if col not in self.columns:
                self.columns[col] = Column(self.num_rows)
            col_row_count = self.columns[col].append(val)
            assert col_row_count == new_row_count

        if id != None:
            self.row_to_id[self.num_rows] = id

        self.num_rows = new_row_count
        return new_row_count

    def query(self, q):
        bs = q.resolve_to_bitset(self)
        set = bs.get_bits()
        return [self.row_to_id[row] for row in set]

    def get_column(self, name):
        return self.columns[name]


class JunctionQuery:
    """A query that wraps two subqueries with a bitwise op"""
    OP_AND = 'AND'
    OP_OR  = 'OR'
    OP_ANDNOT = 'ANDNOT'

    def __init__(self, left, right, operator):
        self.left = left
        self.right = right
        self.op = operator

    def __str__(self):
        return "(%s %s %s)" % (self.left, self.op, self.right)

    def resolve_to_bitset(self, table):
        bs_left = self.left.resolve_to_bitset(table)
        bs_right = self.right.resolve_to_bitset(table)
        
        if self.op == self.OP_AND:
            return bs_left & bs_right

        elif self.op == self.OP_OR:
            return bs_left | bs_right

        elif self.op == self.OP_ANDNOT:
            # this will be optimized later
            return bs_left & (~bs_right)

        else:
            raise Exception("unknown op: " + self.op)

class NotQuery:
    """Inverts its subquery"""
    
    def __init__(self, query):
        self.query = query

    def __str__(self):
        return '(NOT %s)' % str(self.query)

    def resolve_to_bitset(self, table):
        return ~(self.query.resolve_to_bitset(table))


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
    TYPE_NEQ = '!='
    
    def __init__(self, colname, param, type = TYPE_EQ):
        self.colname = colname
        self.type = type
        self.param = param

    def __str__(self):
        return '(%s %s %s)' % (self.colname, self.type, str(self.param))

    def resolve_to_bitset(self, table):
        col = table.get_column(self.colname)
        
        if self.type == self.TYPE_EQ:
            return col.get_index(self.param)
        elif self.type == self.TYPE_LTE:
            return col.get_range_index(None, self.param)
        elif self.type == self.TYPE_GTE:
            return col.get_range_index(self.param, None)
        elif self.type == self.TYPE_NEQ:
            return ~(col.get_index(self.param))


class TableTestCase(unittest.TestCase):
    def setUp(self):
        t = Table()
        t.append_row(1,
                     {'price': 98,
                      'territories': set(['us','ca']),
                      'genres': set(['rock','pop','powerpop'])})
        t.append_row(3,
                     {'price': 45,
                      'territories': set(['us','gb']),
                      'genres': set(['rock','pop','powerpop'])})
        t.append_row(9,
                     {'price': 0,
                      'territories': set(['us','ca']),
                      'genres': set(['emo','powerpop'])})
        t.append_row(15,
                     {'price': 0,
                      'territories': set(['us','ca','gb']),
                      'genres': set(['rock','blues','jazz'])})
        self.t = t

    def testNumRows(self):
        self.assertEqual(self.t.num_rows, 4)

    def testColumnQuery(self):
        q = ColumnQuery("genres", "rock")
        self.assertEqual(self.t.query(q),
                         [1,3,15])

        q = ColumnQuery("price", 1, ColumnQuery.TYPE_GTE)
        self.assertEqual(self.t.query(q),
                         [1,3])

        q = ColumnQuery("price", 1, ColumnQuery.TYPE_LTE)
        self.assertEqual(self.t.query(q),
                         [9,15])

    def testJunctionQuery(self):
        # rock and pop
        q = JunctionQuery(
            ColumnQuery("genres", "rock"),
            ColumnQuery("genres", "pop"),
            JunctionQuery.OP_AND)
        self.assertEqual(self.t.query(q),
                         [1,3])

        # rock or pop
        q = JunctionQuery(
            ColumnQuery("genres", "rock"),
            ColumnQuery("genres", "pop"),
            JunctionQuery.OP_OR)
        self.assertEqual(self.t.query(q),
                         [1,3,15])

    def testNotQuery(self):
        # not rock
        q = NotQuery(ColumnQuery("genres", "rock"))
        self.assertEqual(self.t.query(q),
                         [9])
    

if __name__ == '__main__':
    unittest.main(defaultTest = "TableTestCase")

