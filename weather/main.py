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

from forecastio import ForecastIO
from svgtemplate import SVGTemplate
from grapher import (plot_temp_graph,
                     plot_pop_graph)

config = {
    'output_dir': '.',
}

# configuration options that can also be set on the command line
config_keys = [
    'apikey',
    'location',
    'output_dir',
]

# configuration options for which we cannot provide a default
required_keys = [
    'apikey',
    'location',
]

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
        'attr': '{{{[xlink]}}}href'.format(namespacemap),
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
        'attr': '{{{[xlink]}}}href'.format(namespacemap),
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
    p.add_argument('--output-dir', '-o')
    p.add_argument('--apikey', '-k')
    p.add_argument('--location', '-l')

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

def get_forecast_data():
    logging.debug('getting forecast data')
    f = ForecastIO(config['apikey'],
                   cache_config=config.get('cache_config'))

    data = f.forecast(config['location'])
    return data


def generate_temp_graph(data):
    logging.info('generating temperature graph')
    temp_data = [(h['time'], h['temperature'])
                 for h in data['hourly']['data'][:12]]
    plot_temp_graph(temp_data,
                    output='{[output_dir]}/graph-temp.png'.format(
                        config))


def generate_pop_graph(data):
    logging.info('generating precipitation graph')
    pop_data = [(h['time'], h['precipProbability'])
                for h in data['hourly']['data'][:12]]
    plot_pop_graph(pop_data,
                   output='{[output_dir]}/graph-pop.png'.format(
                       config))


def generate_graphs(data):
    generate_temp_graph(data)
    generate_pop_graph(data)


def generate_svg(data):
    template = SVGTemplate('data/page1.svg')

    filemap = {
        '#graph-temp': {
            'attr': '{{{[xlink]}}}href'.format(namespacemap),
            'value': 'file://{[output_dir]}/graph-temp.png'.format(config),
        },
        '#graph-pop': {
            'attr': '{{{[xlink]}}}href'.format(namespacemap),
            'value': 'file://{[output_dir]}/graph-pop.png'.format(config),
        },
    }

    svg_out = '{[output_dir]}/page1.svg'.format(config)
    png_out = '{[output_dir]}/page1.png'.format(config)
    with open(svg_out, 'w') as fd:
        fd.write(template.render(
            data,
            valuemap,
            filemap))

    subprocess.check_call(['convert', '-colors', '256', '-depth', '8', svg_out, png_out])
    subprocess.check_call(['pngcrush', '-c', '0', '-ow', png_out])

def main():
    global config

    args = parse_args()
    logging.basicConfig(level=args.loglevel)

    with open(args.config) as fd:
        logging.info('reading config from %s',
                     args.config)
        config = yaml.load(fd)
        config = config.get('weather', {})

    for k in config_keys:
        v = getattr(args, k)
        if v is not None:
            config[k] = v

    for k in required_keys:
        if not k in config:
            log.error('missing required configuration option %s',
                      k)
            sys.exit(2)

    config['output_dir'] = os.path.abspath(config['output_dir'])

    data = get_forecast_data()
    generate_graphs(data)
    generate_svg(data)

if __name__ == '__main__':
    f = main()

