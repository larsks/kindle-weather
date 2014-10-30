import logging
import requests
from dogpile.cache import make_region


cacheversion = 2
default_endpoint = 'http://api.forecast.io/forecast'
default_cache_config = {
    'cache.forecast.backend': 'dogpile.cache.memcached',
    'cache.forecast.expiration_time': 3600,
    'cache.forecast.arguments.url': '127.0.0.1:11211',
}

class ForecastIO (object):

    log = logging.getLogger(__name__)

    def __init__(self, apikey,
                 endpoint=default_endpoint,
                 cache_config=None):
        self.apikey = apikey
        self.endpoint = endpoint

        self.cache_config = (
            cache_config if cache_config else default_cache_config)

        self.configure_cache()

    def configure_cache(self):
        self.cache = make_region()
        self.cache.configure_from_config(
            self.cache_config,
            'cache.forecast.',
        )

    def forecast(self, location):
        key = 'weather/{}/forecast/{}'.format(
                cacheversion, location)
        return self.cache.get_or_create(
            key,
            self.rainmaker(location))

    def rainmaker(self, location):
        def _():
            self.log.info('fetching new forecast for %s',
                           location)
            return self._forecast(location)

        return _

    def _forecast(self, location):
        url = '{endpoint}/{apikey}/{location}'.format(
            endpoint=self.endpoint,
            apikey=self.apikey,
            location=location)

        self.log.debug('fetching forecast from %s', url)
        res = requests.get(url)
        self.log.debug('api calls today: %s',
                       res.headers['x-forecast-api-calls'])
        res.raise_for_status()

        data = res.json()

        return data

