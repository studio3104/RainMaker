import threading
import time
from datetime import datetime, timedelta

import numpy
import pandas
from pandas.core.indexes.datetimes import DatetimeIndex

from libraries.exchanges.bitflyer import ChartType, ProductCode, Candlestick
from libraries.exchanges.bitflyer.models import ChartTable


class Chart:
    def __init__(
            self, product_code: ProductCode, candlestick: Candlestick,
            auto_following: bool = True, following_interval: float = 5.0,
            max_num_of_candles: int = numpy.inf,
    ) -> None:

        self._lock = threading.Lock()
        self.__max_num_of_candles = max_num_of_candles
        self.chart_type: ChartType = getattr(ChartType, f'{product_code.name}_{candlestick.name}')

        now = datetime.utcnow()
        condition = ChartTable.period_from <= now
        if isinstance(max_num_of_candles, int) and max_num_of_candles > 0:
            _from = now - timedelta(seconds=(candlestick.value * max_num_of_candles))
            condition = ChartTable.period_from.between(_from, now)
        self.__df = ChartTable.query_as_data_frame(self.chart_type, condition)

        def _continue_following() -> None:
            start_time = time.time()

            while True:
                _t = threading.Thread(target=self.follow_up_to_current)
                _t.start()
                _t.join()

                time_to_wait = ((start_time - time.time()) % following_interval) or following_interval
                time.sleep(time_to_wait)

        if auto_following:
            t = threading.Thread(target=_continue_following)
            t.start()

    @property
    def df(self) -> pandas.DataFrame:
        while self._lock.locked():
            pass
        return self.__df

    def follow_up_to_current(self) -> None:
        self._lock.acquire()

        last_index: DatetimeIndex = self.__df.tail(1).index  # noqa

        d = last_index.date[0]
        t = last_index.time[0]
        dt: datetime = datetime(d.year, d.month, d.day, t.hour, t.minute, t.second)

        newer_df = ChartTable.query_as_data_frame(
            self.chart_type,
            ChartTable.period_from.between(dt, datetime.utcnow()),
        )

        self.__df.drop(index=last_index, inplace=True)
        self.__df = self.__df.append(newer_df)

        if len(self.__df.index) > self.__max_num_of_candles:
            self.__df = self.__df.iloc[-self.__max_num_of_candles:, :]

        self._lock.release()
