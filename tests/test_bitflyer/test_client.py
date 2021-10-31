from typing import Dict, Union

from datetime import datetime, timezone
import json

import pytest
from requests_mock.mocker import Mocker

from lib.exchanges.bitflyer import BitFlyer, Ticker, Pair, State


class TestGetTicker:
    @pytest.mark.parametrize(('mock_response', 'product_code'), (
            (
                    {
                        'best_ask': 6940335.0,
                        'best_ask_size': 0.405,
                        'best_bid': 6936194.0,
                        'best_bid_size': 0.095,
                        'ltp': 6936198.0,
                        'market_ask_size': 0.0,
                        'market_bid_size': 0.0,
                        'product_code': 'BTC_JPY',
                        'state': 'RUNNING',
                        'tick_id': 16248765,
                        'timestamp': '2021-10-31T10:26:34.06',
                        'total_ask_depth': 856.83601465,
                        'total_bid_depth': 681.4649319,
                        'volume': 11559.369918,
                        'volume_by_product': 1740.24096177
                    },
                    Pair.BTC_JPY,
            ),
            (
                    {
                        'best_ask': 485153.0,
                        'best_ask_size': 0.4,
                        'best_bid': 484899.0,
                        'best_bid_size': 0.53,
                        'ltp': 484766.0,
                        'market_ask_size': 0.0,
                        'market_bid_size': 0.0,
                        'product_code': 'ETH_JPY',
                        'state': 'RUNNING',
                        'tick_id': 11839318,
                        'timestamp': '2021-10-31T11:25:00.047',
                        'total_ask_depth': 2022.7817086,
                        'total_bid_depth': 2872.439631,
                        'volume': 14802.8781446,
                        'volume_by_product': 14802.8781446
                    },
                    Pair.ETH_JPY,
            )
    ))
    def test_get_ticker(
            self, mock_response: Dict[str, Union[str, int, float]], product_code: Pair,
            client: BitFlyer, requests_mock: Mocker,
    ) -> None:

        requests_mock.get(
            f'{BitFlyer.URL}/ticker?product_code={product_code.name}',
            text=json.dumps(mock_response),
        )

        response = client.get_ticker(product_code)
        assert isinstance(response, Ticker)

        for k, v in mock_response.items():
            attr = getattr(response, k)

            if k == 'product_code':
                assert attr == getattr(Pair, v)
            elif k == 'state':
                assert attr == getattr(State, '_'.join(v.split()))
            elif k == 'timestamp':
                assert isinstance(attr, datetime)
                assert attr.tzinfo == timezone.utc
            else:
                assert attr == v
