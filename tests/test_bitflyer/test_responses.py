from typing import Any

import pytest

from datetime import datetime

from lib.exchanges.bitflyer import Ticker, Pair, State


class TestTicker:
    @pytest.mark.parametrize('name', (
            'product_code',
            'state',
            'timestamp',
            'tick_id',
            'best_bid',
            'best_ask',
            'best_bid_size',
            'best_ask_size',
            'total_bid_depth',
            'total_ask_depth',
            'market_bid_size',
            'market_ask_size',
            'ltp',
            'volume',
            'volume_by_product',
    ))
    def test_has_field(self, name: str) -> None:
        assert name in Ticker.__dataclass_fields__  # noqa

    @pytest.mark.parametrize(('name', 'data_type'), (
            ('product_code', Pair),
            ('state', State),
            ('timestamp', datetime),
            ('tick_id', int),
    ))
    def test_data_type(self, name: str, data_type: Any) -> None:
        assert Ticker.__dataclass_fields__[name].type is data_type  # noqa

    @pytest.mark.parametrize('name', (
            'best_bid',
            'best_ask',
            'best_bid_size',
            'best_ask_size',
            'total_bid_depth',
            'total_ask_depth',
            'market_bid_size',
            'market_ask_size',
            'ltp',
            'volume',
            'volume_by_product',
    ))
    def test_is_float(self, name: str) -> None:
        assert Ticker.__dataclass_fields__[name].type is float  # noqa
