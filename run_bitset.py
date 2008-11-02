#!/usr/bin/python

from bitset import BitSet
import random
from time import time

def format(bs, num):
    return "".join([str(int(bs[i] > 0)) for i in xrange(0, num)])

def main():
    x = BitSet(1024*1024)
    y = BitSet(1024*1024)

    print "setting bits..."
    for i in random.sample(xrange(1024*1024), 500*1024):
        x[i] = 1

    for i in random.sample(xrange(1024*1024), 500*1024):
        y[i] = 1

    print "x:  ", format(x, 32)
    print "y:  ", format(y, 32)


    print "calculating bitwise or"

    st = time()
    for i in xrange(1, 100):
        z = x | y
    et = time()
    print "done in %f" % ((et - st)/100.0)

    print "x|y:", format(z, 32)

    ##############################

    print "calculating bitwise and"

    st = time()
    for i in xrange(1, 100):
        z = x & y
    et = time()
    print "done in %f" % ((et - st)/100.0)

    print "x&y:", format(z, 32)


if __name__ == '__main__':
    main()

