#!/usr/bin/python

import os
import sys
import argparse
import struct
import logging

EVENT_FORMAT = 'llHHI'
EVENT_SIZE = struct.calcsize(EVENT_FORMAT)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--event', '-e', nargs=4, action='append',
                   default=[])
    p.add_argument('--verbose', '-v',
                   action='store_const',
                   dest='loglevel',
                   const=logging.INFO)
    p.add_argument('--debug', '-d',
                   action='store_const',
                   dest='loglevel',
                   const=logging.DEBUG)
    p.add_argument('device',
                   default='/dev/input/event1')

    p.set_defaults(loglevel=logging.WARN)
    return p.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(
        level = args.loglevel)

    eventmap = {}

    for eventspec in args.event:
        e_type, e_code, e_value, e_script = eventspec
        eventmap['%s:%s:%s' % (e_type, e_code, e_value)] = e_script

    with open(args.device, 'rb') as events:
        while True:
            event = events.read(EVENT_SIZE)
            if not event:
                break

            (tv_sec, tv_usec, type, code, value) = struct.unpack(
                EVENT_FORMAT, event)

            key = '%s:%s:%s' % (type, code, value)

            logging.debug('raw event: %s' % key)
            if not key in eventmap:
                continue

            logging.info('recognized event %s script %s' % (key,
                                                            eventmap[key]))
            os.system(eventmap[key])

if __name__ == '__main__':
    main()


