import pytest

from libraries.exchanges.bitflyer import BitFlyer


@pytest.fixture
def client() -> BitFlyer:
    return BitFlyer()
