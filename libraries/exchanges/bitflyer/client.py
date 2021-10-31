from datetime import datetime
import requests

from .enumerations import Pair, State
from .responses import Ticker


class BitFlyer:
    URL = 'https://api.bitflyer.com/v1'

    def get_ticker(self, pair: Pair) -> Ticker:
        response = requests.get(f'{self.URL}/ticker', params={'product_code': pair.name})
        response.raise_for_status()

        r = response.json()
        timestamp_str = f"{r['timestamp']}+00:00"
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
        except ValueError:
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%f%z')

        return Ticker(**{**r, **{
            'product_code': pair,
            'state': getattr(State, '_'.join(r['state'].split())),
            'timestamp': timestamp,
        }})
