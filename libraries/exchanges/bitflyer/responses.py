from typing import Any, Dict

from dataclasses import dataclass
from datetime import datetime

from .enumerations import ProductCode, State


@dataclass(frozen=True)
class Ticker:
    product_code: ProductCode
    state: State
    timestamp: datetime
    tick_id: int
    best_bid: float
    best_ask: float
    best_bid_size: float
    best_ask_size: float
    total_bid_depth: float
    total_ask_depth: float
    market_bid_size: float
    market_ask_size: float
    ltp: float
    volume: float
    volume_by_product: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Ticker':
        ts: str = data['timestamp']
        if ts.endswith('Z'):
            ts = ts[:-1]
        if (sub := len(ts.split('.')[-1]) - 6) > 0:
            ts = ts[:-sub]
        timestamp_str = f'{ts}+00:00'
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
        except ValueError:
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%f%z')

        return Ticker(**{**data, **{
            'product_code': getattr(ProductCode, data['product_code']),
            'state': getattr(State, '_'.join(data['state'].split())),
            'timestamp': timestamp,
        }})
