import pytest

from lib.exchanges.bitflyer import BitFlyer


@pytest.fixture
def client() -> BitFlyer:
    return BitFlyer()
