from dataclasses import dataclass
from datetime import datetime

from .enumerations import Pair, State


@dataclass(frozen=True)
class Ticker:
    product_code: Pair
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
