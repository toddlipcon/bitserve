#!/usr/bin/python

from bitset import BitSet

import os,sys,time

my_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
sys.path.insert(0, my_dir + '/gen-py')

from bitserve import BitServe
from bitserve.ttypes import *

from thrift.transport import TTransport, TSocket
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from table import Table
from queryparser import Parser

def split_ints(commasep):
    if commasep == '':
        return set()
    return set([int(s) for s in commasep.split(",")])


class BitServeHandler:
    CONVERT_FUNS = {
        LoadType.STRING: (lambda x: x),
        LoadType.CENTS_FLOAT: (lambda x: int(float(x)*100)),
        LoadType.JOINED_INTS: split_ints,
        LoadType.INT: (lambda x: int(x))
        }

    def __init__(self):
        self.tables = {}
        self.parser = Parser()

    def load_table(self, name, path, columns):
        t = Table()
        seen_header = False

        # Find the pk and other fields
        pk = None
        fields = []
        idx = 0
        for (idx, colspec) in enumerate(columns):
            colspec.idx = idx

            # attach a convert function
            colspec.convert = self.CONVERT_FUNS[colspec.type]

            if colspec.is_primary_key:
                if pk:
                    raise TApplicationException(
                        "too many pks: %s and %s" % (pk.name, colspec.name)
                        )
                pk = colspec
            else:
                fields.append(colspec)

        print "Loading table %s from %s" % (name, path)
        for (lineno, line) in enumerate(file(path)):
            if not seen_header:
                seen_header = True
                continue

            linefields = line.rstrip("\n").split("\t")
            data = {}
            for field in fields:
                data[field.name] = field.convert(linefields[field.idx])
            pk_val = pk.convert(linefields[pk.idx])

            t.append_row(pk_val, data)

            if lineno % 1000 == 0:
                print "loaded %d lines" % lineno

        self.tables[name] = t
        print "Finished loading %d rows into table %s" % (t.num_rows, name)
        return t.num_rows

    
    def query(self, table, query):
        if table not in self.tables:
            raise NoSuchTableException()

        try:
            st = time.time()
            q = self.parser.parse(query)
            et = time.time()
            print "parse time: %fms" % ((et - st)*1000)
        except Exception, e:
            print str(e)
            raise ParseException({'message': str(e)})

        st = time.time()
        res = self.tables[table].query(q)
        et = time.time()
        print "execution time: %fms" % ((et - st)*1000)
        print "%d results" % len(res)
        return res
    
def load_albums_5k(handler):
    handler.load_table(
        "albums_5k",
        "../albums_5k.tsv",
        [LoadColumn({'is_primary_key': 1,
                     'name':"id",
                     'type': LoadType.INT}),
         LoadColumn({'name': "status"}),
         LoadColumn({'name': "price",
                     'type': LoadType.CENTS_FLOAT}),
         LoadColumn({'name': "genre",
                     'type': LoadType.JOINED_INTS}),
         LoadColumn({'name': "policy",
                     'type': LoadType.STRING}),
         LoadColumn({'name': "country",
                     'type': LoadType.JOINED_INTS})])

def main(port=9400):
    handler = BitServeHandler()


    load_albums_5k(handler)

    processor = BitServe.Processor(handler)
    transport = TSocket.TServerSocket(port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)
    server.serve()


if __name__ == '__main__':
    main()
