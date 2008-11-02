from bitset import BitSet

class Column:
    def __init__(self):
        self.indices = {}
        self.num_rows = 0

    def get_index(self, value):
        return self.indices[value]

    def get_range_index(self, minval, maxval):
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
        need_new = True

        self.num_rows += 1
        
        for (existing_val, bs) in self.indices.iteritems():
            if existing_val == value:
                bs += 1
                need_new = False
            else:
                bs += 0

        # if we didn't find a bitset for this value, make a new one
        if need_new:
            new_bs = BitSet(self.num_rows)
            new_bs[self.num_rows - 1] = 1
            self.indices[value] = new_bs

        return self.num_rows

def test():
    x = BitSet(0)
    x += 0
    x += 1
    x += 1
    print x

    col = Column()

    vals = [1,2,3,2,4,5,0]
    for val in vals:
        col.append(val)

    twos = col.get_index(2)
    print twos

    my_range = col.get_range_index(2, 4)
    print my_range
    


if __name__ == '__main__':
    test()
