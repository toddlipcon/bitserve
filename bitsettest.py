#!/usr/bin/env python
#
# Unit tests for bitset extension

from bitset import BitSet

import unittest

class BitSetTestCase(unittest.TestCase):

    def makeSet(self, vals):
        x = BitSet(len(vals))
        for val in vals:
            x += val
        return x
    
    def testGetSet(self):
        x = BitSet(16)
        x[0] = 1
        x[3] = 0
        assert x[0], "got bit set"
        assert not x[3], "got bit not set"

    def testLength(self):
        x = BitSet(0)
        assert len(x) == 0, "0 length before setting"
        x[20] = 0
        self.assertEqual(len(x), 21)
        x[10] = 1
        self.assertEqual(len(x), 21)


        x = BitSet(0)
        i = 0
        for val in [1,1,1,0,0,1,0,0,1,0,0,1,0]:
            self.assertEqual(len(x), i)
            i += 1
            x += val

    def testStr(self):
        x = BitSet()
        self.assertEqual(str(x), "")
        x[0] = 1
        self.assertEqual(str(x), "1")
        x[3] = 1
        self.assertEqual(str(x), "1001")
        x[5] = 1
        self.assertEqual(str(x), "100101")

        # Test appending one by one
        x = BitSet(0)
        expect_str = ""
        for val in [1,1,1,0,0,1,0,0,1,0,0,1,0]:
            self.assertEqual(str(x), expect_str)
            expect_str += str(val)
            x += val


    def testAppend(self):
        x = self.makeSet([1])
        self.assertEqual(str(x), "1")

        y = self.makeSet([1,0,0,1,0,0,1,0,0,0,1,0,0])
        self.assertEqual(str(y), "1001001000100")

        z = self.makeSet([1,0,0,1,1,0,1,0,1,0,1,0,0,1,0])
        self.assertEqual(str(z), "100110101010010")


    def testOr(self):
        # Test same size
        x = self.makeSet([1,0,0,1,0,0,1,0,0,0,1,0,0])
        y = self.makeSet([1,0,0,0,1,0,1,0,1,0,1,0,0])
        z = self.makeSet([1,0,0,1,1,0,1,0,1,0,1,0,0])

        self.assertEqual(str(x | y), str(z))
        self.assertEqual(str(y | x), str(z))

        # Test one bigger
        x = self.makeSet([1,0,0,1,0,0,1,0,0,0,1,0,0,1,0])
        y = self.makeSet([1,0,0,0,1,0,1,0,1,0,1,0,0])
        z = self.makeSet([1,0,0,1,1,0,1,0,1,0,1,0,0,1,0])

        self.assertEqual(str(x | y), str(z))
        self.assertEqual(str(y | x), str(z))

        # Test one empty
        x = self.makeSet([])
        y = self.makeSet([1,0,0,0,1,0,1,0,1,0,1,0,0])
        z = self.makeSet([1,0,0,0,1,0,1,0,1,0,1,0,0])

        self.assertEqual(str(x | y), str(z))
        self.assertEqual(str(y | x), str(z))

    def testAnd(self):
        # Test same size
        x = self.makeSet([1,0,0,1,0,0,1,0,0,0,1,0,0])
        y = self.makeSet([1,0,0,0,1,0,1,0,1,0,1,0,0])
        z = self.makeSet([1,0,0,0,0,0,1,0,0,0,1,0,0])

        self.assertEqual(str(x & y), str(z))
        self.assertEqual(str(y & x), str(z))

        # Test one bigger
        x = self.makeSet([1,0,0,1,0,0,1,0,0,0,1,0,0,1,0])
        y = self.makeSet([1,0,0,0,1,0,1,0,1,0,1,0,0])
        z = self.makeSet([1,0,0,0,0,0,1,0,0,0,1,0,0,0,0])

        self.assertEqual(str(x & y), str(z))
        self.assertEqual(str(y & x), str(z))

        # Test one empty
        x = self.makeSet([])
        y = self.makeSet([1,0,0,0,1,0,1,0,1,0,1,0,0])
        z = self.makeSet([0,0,0,0,0,0,0,0,0,0,0,0,0])

        self.assertEqual(str(x & y), str(z))
        self.assertEqual(str(y & x), str(z))
        
    def testInvert(self):
        x = self.makeSet([0,1,0,0,1])
        y = ~x
        self.assertEqual(str(y), "10110")

        # Extend it and make sure the "hidden" bits didn't get set to 1s
        y[15] = 1
        self.assertEqual(str(y), "1011000000000001")

    def testGetBits(self):
        def dotest(l):
            l.sort()
            x = BitSet()
            for i in l:
                x[i] = 1
            self.assertEqual(x.get_bits(), l)

        dotest([0,3,5,8])
        dotest([23,54,1,29])
        



def suite():
    return unittest.makeSuite(BitSetTestCase)

if __name__ == "__main__":
    unittest.main()
