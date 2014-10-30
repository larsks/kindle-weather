#!/usr/bin/python

import os
import sys
import argparse
import yaml
import logging
import jsonpointer
import time
from lxml import etree, cssselect
import subprocess
from pkg_resources import (Requirement,
                           resource_filename,
                           resource_stream)

from forecastio import ForecastIO
from grapher import (plot_temp_graph,
                     plot_pop_graph)

def attr_setter(attr):
    def _(ele, val):
        ele.set(attr, val)

    return _

namespacemap = {
    'xlink': 'http://www.w3.org/1999/xlink',
}

iconmap = {
    'rain': 'ra',
    'partly-cloudy-day': 'few',
    'partly-cloudy-night': 'few',
    'cloudy': 'ovc',
}

valuemap = {
    '/daily/data/0/temperatureMax': {
        'selector': '#day_0_high',
        'format': lambda x: str(int(round(x))),
    },
    '/daily/data/0/temperatureMin': {
        'selector': '#day_0_low',
        'format': lambda x: str(int(round(x))),
    },
    '/daily/data/0/precipProbability': {
        'selector': '#day_0_pop',
        'format': lambda x: str(int(round(x*100))),
    },
    '/daily/data/0/icon': {
        'selector': '#day_0_icon',
        'format': lambda x: '#{}'.format(iconmap.get(x, 'unknown')),
        'setter': attr_setter('{{{[xlink]}}}href'.format(namespacemap)),
    },

    '/daily/data/1/temperatureMax': {
        'selector': '#day_1_high',
        'format': lambda x: str(int(round(x))),
    },
    '/daily/data/1/temperatureMin': {
        'selector': '#day_1_low',
        'format': lambda x: str(int(round(x))),
    },
    '/daily/data/1/precipProbability': {
        'selector': '#day_1_pop',
        'format': lambda x: str(int(round(x*100))),
    },
    '/daily/data/1/icon': {
        'selector': '#day_1_icon',
        'format': lambda x: '#{}'.format(iconmap.get(x, 'unknown')),
        'setter': attr_setter('{{{[xlink]}}}href'.format(namespacemap)),
    },

    '/currently/time': {
        'selector': '#last_updated_at',
        'format': lambda x: time.strftime('%Y-%m-%d %H:%M', 
                                          time.localtime(x)),
    },
}

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--config', '-f',
                   default='weather.yaml')
    p.add_argument('--output-dir', '-o',
                   default='output')

    g = p.add_argument_group('Logging')
    g.add_argument('--debug', '-d',
                   action='store_const',
                   const=logging.DEBUG,
                   dest='loglevel')
    g.add_argument('--verbose', '-v',
                   action='store_const',
                   const=logging.INFO,
                   dest='loglevel')

    p.set_defaults(loglevel=logging.WARN)
    return p.parse_args()

def main():
    global config

    args = parse_args()
    logging.basicConfig(level=args.loglevel)

    with open(args.config) as fd:
        logging.info('reading config from %s',
                     args.config)
        config = yaml.load(fd)

    config['weather'].setdefault('output_dir', args.output_dir)

    svg_template = resource_stream(__name__,
                                     'data/page1.svg')
    doc = etree.parse(svg_template)
    svg_template.close()

    f = ForecastIO(config['weather']['apikey'],
                   cache_config=config['weather'].get('cache_config'))
    
    data = f.forecast(config['weather']['location'])
    temp_data = [(h['time'], h['temperature'])
                 for h in data['hourly']['data'][:12]]
    pop_data = [(h['time'], h['precipProbability'])
                for h in data['hourly']['data'][:12]]

    plot_temp_graph(temp_data,
                    output='{[weather][output_dir]}/graph-temp.png'.format(
                        config))
    plot_pop_graph(pop_data,
                    output='{[weather][output_dir]}/graph-pop.png'.format(
                        config))

    for t in ['temp', 'pop']:
        sel = cssselect.CSSSelector('#graph-{}'.format(t))
        ele = sel(doc)
        if not ele:
            logging.error('selector %s failed to locate an element',
                         sel)
            raise ValueError(sel)
        ele = ele[0]
        ele.set('{{{[xlink]}}}href'.format(namespacemap),
                'file://{}/{}'.format(
                    os.path.abspath(config['weather']['output_dir']),
                    'graph-{}.png'.format(t)
                ))

    for jp,spec in valuemap.items():
        val = jsonpointer.resolve_pointer(data, jp)
        val = spec['format'](val)
        sel = cssselect.CSSSelector(spec['selector'])
        ele = sel(doc)
        if not ele:
            logging.error('failed to locate selector "%s" in template',
                          spec['selector'])
            raise KeyError(spec['selector'])
        if len(ele) > 1:
            logging.error('selector "%s" does not return a unique result',
                          spec['selector'])
            raise ValueError(spec['selector'])

        ele = ele[0]

        if 'setter' in spec:
            spec['setter'](ele, val)
        else:
            ele.text = val

    with open('%s/page1.svg' % config['weather']['output_dir'], 'w') as fd:
        doc.write(fd)

    os.chdir(config['weather']['output_dir'])
    logging.info('generating output image')
    subprocess.check_call(['convert', 'page1.svg', 'page1.png'])
    logging.info('collapsing png colorspace')
    subprocess.check_call(['pngcrush', '-c', '0', '-ow', 'page1.png'])

if __name__ == '__main__':
    f = main()

