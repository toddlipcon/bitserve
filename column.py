#!/usr/bin/env python
#
# Represents a column that is indexed by bitset indexes

from bitset import BitSet

import unittest

class Column:
    def __init__(self, num_rows = 0):
        self.indices = {}
        self.num_rows = num_rows

    def get_index(self, value):
        """Returns the bitset for the given value, or throws KeyError
        if it does not exist."""
        return self.indices[value]

    def get_range_index(self, minval, maxval):
        """Returns a bitset with 1s in any position where the value
        falls between minval and maxval according to the python
        comparison operators."""
        
        bitsets = []
        for (val, bs) in self.indices.iteritems():
            if ((minval == None or val >= minval) and
                (maxval == None or val <= maxval)):
                bitsets.append(bs)

        if len(bitsets) == 0:
            return BitSet(0)
        else:
            res = bitsets.pop()
            for bs in bitsets:
                res |= bs
            return res

    def append(self, value):
        """Append a new row with the given value. Creates a new bitset
        if this value hasn't been seen before."""

        if type(value) == set:
            return self.append_set(value)
        else:
            return self.append_set(set([value]))

    def append_set(self, values):
        """Append a new row that has a set-typed value. Creates new bitsets
        for any values that haven't been seen before.

        The values parameter should be a python set() type.
        """

        self.num_rows += 1

        remaining = set(values) # copy it
        for (existing_val, bs) in self.indices.iteritems():
            if existing_val in remaining:
                remaining.discard(existing_val)
                bs += 1
            else:
                bs += 0

        for new_val in remaining:
            new_bs = BitSet(self.num_rows)
            new_bs[self.num_rows - 1] = 1
            self.indices[new_val] = new_bs

        return self.num_rows

class ColumnTestCase(unittest.TestCase):
    def testBasic(self):
        col = Column()

        vals = [1,2,3,2,4,5,0]
        for val in vals:
            col.append(val)

        self.assertEqual(str(col.get_index(2)),
                         "0101000")
        self.assertEqual(str(col.get_range_index(2,4)),
                         "0111100")

    def testSet(self):
        col = Column()

        col.append_set(['us','ca','gb'])
        col.append_set(['us','za','au'])
        col.append_set(['za','ca'])
        col.append_set([])

        self.assertEqual(str(col.get_index('us')),
                         "1100")
        self.assertEqual(str(col.get_index('ca')),
                         "1010")
        

if __name__ == '__main__':
    unittest.main(defaultTest = "ColumnTestCase")
