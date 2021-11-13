import threading
import time
from datetime import datetime

import pandas
from pandas.core.indexes.datetimes import DatetimeIndex

from libraries.exchanges.bitflyer import ChartType, ProductCode, Candlestick
from libraries.exchanges.bitflyer.models import ChartTable


class Chart:
    def __init__(
            self, product_code: ProductCode, candlestick: Candlestick,
            auto_following: bool = True, following_interval: float = 10.0,
    ) -> None:
        self.chart_type: ChartType = getattr(ChartType, f'{product_code.name}_{candlestick.name}')
        self.__df = ChartTable.query_as_data_frame(self.chart_type, ChartTable.period_from <= datetime.utcnow())

        self._lock = threading.Lock()

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

        self._lock.release()
