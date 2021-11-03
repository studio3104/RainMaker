from typing import Dict, Optional

import logging
import threading
import time

import numpy
import talib

from collections import deque

from libraries.exchanges.bitflyer import BitFlyer, ProductCode

bf = BitFlyer()

logger = logging.getLogger(__name__)

ticker_logger = logging.getLogger('ticker')
ticker_logger.setLevel(logging.DEBUG)
ticker_logger.addHandler(logging.FileHandler(filename='ticker.log'))

tx_logger = logging.getLogger('transaction')
tx_logger.setLevel(logging.DEBUG)
tx_logger.addHandler(logging.StreamHandler())
tx_logger.addHandler(logging.FileHandler(filename='transaction.log'))


class Processor:
    def __init__(self) -> None:
        self.ltp = deque(maxlen=15)

        self.profits: Dict[float, float] = {}
        self.positions: Dict[float, Optional[float]] = {}

    def process(self) -> None:
        try:
            self._process()
        except Exception as e:
            logger.error(e)

    def _process(self) -> None:
        ticker = bf.get_ticker(ProductCode.BTC_JPY)
        diff = ticker.ltp - self.ltp[-1] if self.ltp else 0.0
        timestamp = ticker.timestamp.timestamp()
        lb = {'tick_id': ticker.tick_id, 'timestamp': timestamp, 'ltp': ticker.ltp, 'diff': diff, 'rsi': None}

        self.ltp.append(ticker.ltp)
        if len(self.ltp) < 15:
            ticker_logger.info(lb)
            return

        rsi = talib.RSI(numpy.array(self.ltp), timeperiod=14)[-1]
        ticker_logger.info({**lb, **{'rsi': rsi}})

        for n in range(1, 31):
            self.transact(ticker.ltp, rsi, timestamp, n / 10)

    def transact(self, price: float, rsi: float, timestamp: float, loss_cut_rate: float) -> None:
        if loss_cut_rate not in self.positions:
            self.positions[loss_cut_rate] = None
        if loss_cut_rate not in self.profits:
            self.profits[loss_cut_rate] = 0.0

        position = self.positions[loss_cut_rate]
        fee = price * 0.0015
        lb = {'timestamp': timestamp, 'lossCutRate': loss_cut_rate, 'price': price, 'fee': fee}

        if position is None:
            if rsi < 30:
                self.positions[loss_cut_rate] = price
                self.profits[loss_cut_rate] -= (price + fee)
                tx_logger.info({**lb, **{'action': 'BUY', 'profit': self.profits[loss_cut_rate]}})
            return

        to_sell = False
        reason = ''

        if position * (100 - loss_cut_rate) / 100 >= price:
            to_sell = True
            reason = 'LossCut'

        if position * (100 + loss_cut_rate * 1.5) / 100 <= price:
            to_sell = True
            reason = 'Profit'

        if to_sell:
            self.positions[loss_cut_rate] = None
            self.profits[loss_cut_rate] += (price - fee)
            tx_logger.info({**lb, **{'action': 'SELL', 'reason': reason, 'profit': self.profits[loss_cut_rate]}})


processor = Processor()


def run() -> None:
    interval = 10
    start_time = time.time()

    while True:
        t = threading.Thread(target=processor.process())
        t.start()
        t.join()

        time_to_wait = ((start_time - time.time()) % interval) or interval
        time.sleep(time_to_wait)


if __name__ == '__main__':
    run()
