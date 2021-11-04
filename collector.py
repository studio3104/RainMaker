import logging
import dataclasses

from libraries.exchanges.bitflyer import BitFlyerRealTime, Ticker, PublicChannel, ProductCode
from libraries.exchanges.bitflyer.models import TickerTable

logging.basicConfig(level=logging.INFO)

client = BitFlyerRealTime()


def _handler(ticker: Ticker) -> None:
    t = TickerTable(**dataclasses.asdict(ticker))
    t.save()


def run() -> None:
    client.subscribe(PublicChannel.lightning_ticker, ProductCode.BTC_JPY, _handler)
    client.start()


if __name__ == '__main__':
    run()