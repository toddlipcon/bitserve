#!/usr/bin/python

from shell import QueryShell
from table import Table

import sys

def main():
    t = load_table(sys.argv[1])
    run_shell(t)

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

def run_shell(t):
    QueryShell(t).cmdloop()

if __name__ == '__main__':
    if True:
        main()
    else:
        import hotshot
        prof = hotshot.Profile('tsv_test_stats')
        prof.runcall(main)
        prof.close()
        
        
