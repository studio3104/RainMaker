import pytest

from libraries.exchanges.bitflyer import ProductCode, State


class TestPair:
    @pytest.mark.parametrize('name', (
            'BTC_JPY',
            'XRP_JPY',
            'ETH_JPY',
            'XLM_JPY',
            'MONA_JPY',
            'ETH_BTC',
            'BCH_BTC',
    ))
    def test_hasattr(self, name: str) -> None:
        assert hasattr(ProductCode, name)


class TestState:
    @pytest.mark.parametrize('name', (
            'RUNNING',
            'CLOSED',
            'STARTING',
            'PREOPEN',
            'CIRCUIT_BREAK',
            'AWAITING_SQ',
            'MATURED',
    ))
    def test_hasattr(self, name: str) -> None:
        assert hasattr(State, name)
