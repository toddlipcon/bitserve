#!/usr/bin/env python

from cmd import Cmd
from table import Table
from queryparser import Parser

from table import Table, JunctionQuery, ColumnQuery, MultiJunctionQuery

import time
import traceback
import sys

class QueryShell(Cmd):
    def __init__(self, table):
        Cmd.__init__(self)
        self.table = table
        self.parser = Parser()
    
    def do_select(self, cmd):
        try:
            t1 = time.time()
            q = self.parser.parse(cmd)
            t2 = time.time()
            res = self.table.query(q)
            t3 = time.time()

            print "query parsed: ", q
            print "Parse time (ms): ", ((t2 - t1)*1000)
            print "Exec  time (ms): ", ((t3 - t2)*1000)

            print "%d results:", len(res)
            print 
            print res
            
        except Exception, e:
            print "exception: ", e
            traceback.print_exc(file=sys.stdout)
            
    def do_bench(self, junk):
        t = self.table
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




def main():
    t = Table()

    s = QueryShell(t)
    s.cmdloop()


if __name__ == '__main__':
    main()
