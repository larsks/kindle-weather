#!/usr/bin/python

import os
import sys
import argparse
import yaml
import logging
import time
import subprocess
import pytz

from forecastio import ForecastIO
from svgtemplate import SVGTemplate
from grapher import (plot_temp_graph,
                     plot_pop_graph)

config = {
    'output_dir': '.',
    'timezone': pytz.utc,
    'number_of_hours': 12,
}

# configuration options that can also be set on the command line
config_keys = [
    'apikey',
    'location',
    'output_dir',
    'number_of_hours',
]

# configuration options for which we cannot provide a default
required_keys = [
    'apikey',
    'location',
]

namespaces = {
    'xlink': 'http://www.w3.org/1999/xlink',
    'svg': 'http://www.w3.org/2000/svg',
}

iconmap = {
    'clear-day': 'skc',
    'clear-night': 'skc',
    'cloudy': 'ovc',
    'partly-cloudy-day': 'few',
    'partly-cloudy-night': 'few',
    'rain': 'ra',
    'snow': 'sn',
    'wind': 'wind',
}


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--config', '-f',
                   default='weather.yaml')
    p.add_argument('--output-dir', '-o')
    p.add_argument('--apikey', '-k')
    p.add_argument('--location', '-l')
    p.add_argument('--number-of-hours', '-n')

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
                 for h in
                 data['hourly']['data'][:int(config['number_of_hours'])]]
    plot_temp_graph(temp_data,
                    output='{[output_dir]}/graph-temp.png'.format(
                        config),
                    tz=pytz.timezone(config['timezone']))


def generate_pop_graph(data):
    logging.info('generating precipitation graph')
    pop_data = [(h['time'], h['precipProbability'])
                for h in
                data['hourly']['data'][:int(config['number_of_hours'])]]
    plot_pop_graph(pop_data,
                   output='{[output_dir]}/graph-pop.png'.format(
                       config),
                   tz=pytz.timezone(config['timezone']))


def generate_graphs(data):
    generate_temp_graph(data)
    generate_pop_graph(data)


def postprocess(svg_out, png_out):
    subprocess.check_call(['convert', '-colors', '256',
                           '-depth', '8', svg_out, png_out])
    subprocess.check_call(['pngcrush', '-q', '-c', '0', '-ow', png_out])


def generate_page1(data):
    logging.debug('generating svg page 1')
    template = SVGTemplate('data/page1.svg',
                           namespaces=namespaces)

    p1map = {
        '/currently/time': {
            'selector': '#last_updated_at',
            'format': lambda x: time.strftime('%Y-%m-%d %H:%M',
                                              time.localtime(x)),
        },
    }
    for day in [0, 1]:
        p1map['/daily/data/{}/time'.format(day)] = {
            'selector': '#day_{}_label svg|tspan'.format(day),
            'format': lambda x: time.strftime('%A',
                                              time.localtime(x)),
        }
        p1map['/daily/data/{}/temperatureMax'.format(day)] = {
            'selector': '#day_{}_high'.format(day),
            'format': lambda x: str(int(round(x))),
        }
        p1map['/daily/data/{}/temperatureMin'.format(day)] = {
            'selector': '#day_{}_low'.format(day),
            'format': lambda x: str(int(round(x))),
        }
        p1map['/daily/data/{}/precipProbability'.format(day)] = {
            'selector': '#day_{}_pop'.format(day),
            'format': lambda x: str(int(round(x*100))),
        }
        p1map['/daily/data/{}/icon'.format(day)] = {
            'selector': '#day_{}_icon svg|use'.format(day),
            'format': lambda x: '#{}'.format(iconmap.get(x, 'unknown')),
            'attr': '{{{[xlink]}}}href'.format(namespaces),
        }

    svg_out = '{[output_dir]}/page1.svg'.format(config)
    png_out = '{[output_dir]}/page1.png'.format(config)
    with open(svg_out, 'w') as fd:
        fd.write(template.render(
            data,
            p1map,
            {}))

    postprocess(svg_out, png_out)


def generate_page2(data):
    logging.debug('generating svg page 2')
    template = SVGTemplate('data/page2.svg',
                           namespaces=namespaces)

    p2map = {
        '/currently/time': {
            'selector': '#last_updated_at',
            'format': lambda x: time.strftime('%Y-%m-%d %H:%M',
                                              time.localtime(x)),
        },
    }

    for day in [2, 3, 4, 5]:
        p2map['/daily/data/{}/time'.format(day)] = {
            'selector': '#day_{}_label svg|tspan'.format(day),
            'format': lambda x: time.strftime('%A',
                                              time.localtime(x)),
        }
        p2map['/daily/data/{}/temperatureMax'.format(day)] = {
            'selector': '#day_{}_high'.format(day),
            'format': lambda x: str(int(round(x))),
        }
        p2map['/daily/data/{}/temperatureMin'.format(day)] = {
            'selector': '#day_{}_low'.format(day),
            'format': lambda x: str(int(round(x))),
        }
        p2map['/daily/data/{}/precipProbability'.format(day)] = {
            'selector': '#day_{}_pop'.format(day),
            'format': lambda x: str(int(round(x*100))),
        }
        p2map['/daily/data/{}/icon'.format(day)] = {
            'selector': '#day_{}_icon svg|use'.format(day),
            'format': lambda x: '#{}'.format(iconmap.get(x, 'unknown')),
            'attr': '{{{[xlink]}}}href'.format(namespaces),
        }

    svg_out = '{[output_dir]}/page2.svg'.format(config)
    png_out = '{[output_dir]}/page2.png'.format(config)
    with open(svg_out, 'w') as fd:
        fd.write(template.render(
            data,
            p2map,
            {}))

    postprocess(svg_out, png_out)


def generate_svg(data):
    logging.debug('generating svg output')
    generate_page1(data)
    generate_page2(data)


def main():
    global config

    args = parse_args()
    logging.basicConfig(level=args.loglevel)

    with open(args.config) as fd:
        logging.info('reading config from %s',
                     args.config)
        config_from_file = yaml.load(fd)
        config.update(config_from_file.get('weather', {}))

    for k in config_keys:
        v = getattr(args, k)
        if v is not None:
            config[k] = v

    for k in required_keys:
        if k not in config:
            logging.error('missing required configuration option %s',
                          k)
            sys.exit(2)

    config['output_dir'] = os.path.abspath(config['output_dir'])

    logging.debug('config = %s', config)

    data = get_forecast_data()
    generate_graphs(data)
    generate_svg(data)

if __name__ == '__main__':
    f = main()
