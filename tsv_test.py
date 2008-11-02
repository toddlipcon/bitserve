#!/usr/bin/python

from table import Table, JunctionQuery, ColumnQuery, MultiJunctionQuery
import sys
import time
def main():
    t = load_table(sys.argv[1])
    try_queries(t)

def load_table(filename):
    t = Table()

    seen_header = False
    for line in file(filename):
        if not seen_header:
            seen_header = True
            continue

        line = line.rstrip("\n")
        (id, status, price, genres, policy, countries) = line.split("\t")

        def split_ints(commasep):
            if commasep == '':
                return set()
            return set([int(s) for s in commasep.split(",")])

        t.append_row({
            'status': status,
            'price': int(float(price)*100),
            'genre': split_ints(genres),
            'policy': policy,
            'country': split_ints(countries)
            })

    return t

def try_queries(t):
    # Come up with the disjunction for all of the genres we care abotu
    genre_qs = [ColumnQuery('genre', id) for id in [59, 60]]
    genre_set_q = MultiJunctionQuery(genre_qs, JunctionQuery.OP_OR)

    status_q = ColumnQuery('status', 'NORMAL')
    free_q = ColumnQuery('price', 0)

    q = MultiJunctionQuery([genre_set_q, free_q, status_q],
                                     JunctionQuery.OP_AND)

    st = time.time()
    for i in xrange(1000):
        res = t.query(q)
    et = time.time()
    
    print "query time: %fms" % (et - st)


if __name__ == '__main__':
    if True:
        main()
    else:
        import hotshot
        prof = hotshot.Profile('tsv_test_stats')
        prof.runcall(main)
        prof.close()
        
        
