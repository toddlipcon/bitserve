#!/usr/bin/env python

import simplejson
import unittest
from table import ColumnQuery, JunctionQuery, MultiJunctionQuery, NotQuery

class JsonParser:
    JUNCTION_OP_MAP = {
        'and': JunctionQuery.OP_AND,
        'or': JunctionQuery.OP_OR
        }

    COLUMN_OP_MAP = {
        '=': ColumnQuery.TYPE_EQ,
        '!=': ColumnQuery.TYPE_NEQ,
        '>=': ColumnQuery.TYPE_GTE,
        '<=': ColumnQuery.TYPE_LTE
        }


    def parse(self, string):
        obj = simplejson.loads(string)
        return self.visit(obj)


    def visit_junction(self, op, args):
        subqs = [self.visit(a) for a in args]
        return MultiJunctionQuery(subqs, self.JUNCTION_OP_MAP[op.lower()])

    def visit_not(self, arg):
        return NotQuery(self.visit(arg))

    def visit_comparison(self, op, column, value):
        return ColumnQuery(column, value, self.COLUMN_OP_MAP[op])


    def visit_in(self, column, vals):
        queries = [ColumnQuery(column, val) for val in vals]
        return MultiJunctionQuery(queries, JunctionQuery.OP_OR)


    def visit(self, obj):
        if len(obj) >= 3 and self.JUNCTION_OP_MAP.has_key(obj[0]):
            return self.visit_junction(obj[0], obj[1:])
        elif len(obj) == 3 and self.COLUMN_OP_MAP.has_key(obj[0]):
            return self.visit_comparison(*obj)
        elif len(obj) == 3 and obj[0] == 'in':
            return self.visit_in(obj[1], obj[2])
        elif len(obj) == 2 and obj[0] == 'not':
            return self.visit_not(obj[1])
        else:
            raise Exception("bad parse tree element: " + repr(obj))
    


class JsonParserTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = JsonParser()

    def check(self, json, out):
        self.assertEqual(str(self.parser.parse(json)), out)
        
    def testEqual(self):
        self.check('["=", "a", 2]', "(a = 2)")

    def testAnd(self):
        self.check('["and",["=", "a", 2],["!=", "b", "c"]]',
                   '((a = 2) AND (b != c))')

    def testIn(self):
        self.check('["in", "a", [1,2,3]]',
                   "(((a = 1) OR (a = 2)) OR (a = 3))")

    def testNot(self):
        self.check('["not", ["<=", "a", 2]]',
                   "(NOT (a <= 2))")

if __name__ == '__main__':
    unittest.main(defaultTest = "JsonParserTestCase")
