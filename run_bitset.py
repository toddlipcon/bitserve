#!/usr/bin/python

from bitset import BitSet
import random
from time import time

x = BitSet(1024*1024)
y = BitSet(1024*1024)

print "setting bits..."

for i in xrange(1, 500*1024):
    x[random.randint(0, 1024*1024)] = 1
    y[random.randint(0, 1024*1024)] = 1

print "calculating bitwise or"
st = time()
for i in xrange(1, 100):
    z = x | y
et = time()
print [z[i] for i in xrange(0,8)]
print "done in %f" % ((et - st)/100.0)
