#!/usr/bin/python

import os
import sys
import argparse
import json
import time

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--column', '-c',
                   action='append',
                   default=[])
    p.add_argument('--hourly', '-H',
                   action='store_const',
                   dest='data_key',
                   const='hourly')
    p.add_argument('--daily', '-D',
                   action='store_const',
                   dest='data_key',
                   const='daily')
    p.add_argument('--limit', '-l',
                   type=int,
                   default=0)
    p.add_argument('--delimiter', '-d',
                   default=' ')
    p.add_argument('input')
    return p.parse_args()

def main():
    args = parse_args()

    with open(args.input) as fd:
        data = json.load(fd)

    for i,m in enumerate(data[args.data_key]['data']):
        if args.limit and i >= args.limit:
            break

        print args.delimiter.join(str(m[x]) for x in args.column)

if __name__ == '__main__':
    main()


