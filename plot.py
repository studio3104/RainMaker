from typing import List

import pandas
import numpy
import mplfinance

from libraries.exchanges.bitflyer import ChartType
from libraries.exchanges.bitflyer.models import ChartTable


def is_support(df: pandas.DataFrame, i: int) -> bool:
    return (
            df['Low'][i] < df['Low'][i - 1] < df['Low'][i - 2] and
            df['Low'][i] < df['Low'][i + 1] < df['Low'][i + 2]
    )


def is_resistance(df: pandas.DataFrame, i: int) -> bool:
    return (
            df['High'][i] > df['High'][i - 1] > df['High'][i - 2] and
            df['High'][i] > df['High'][i + 1] > df['High'][i + 2]
    )


def is_far_from_level(mean: numpy.float64, level: int, levels: List[int]) -> bool:
    return numpy.sum([abs(level - x) < mean for x in levels]) == 0


def detect_levels(df: pandas.DataFrame) -> List[int]:
    levels = []
    mean = numpy.mean(df['High'] - df['Low'])
    for i in range(2, df.shape[0] - 2):
        level = None
        if is_support(df, i):
            level = int(df['Low'][i])
        if is_resistance(df, i):
            level = int(df['High'][i])

        if level is not None and is_far_from_level(mean, level, levels):
            levels.append(level)

    return levels


def create_data_frame_from_ddb(chart_type: ChartType) -> pandas.DataFrame:
    data = []
    index = []
    q = ChartTable.query(chart_type)

    for c in q:
        index.append(c.period_from)
        data.append({
            'Open': c.open_value,
            'High': c.high_value,
            'Low': c.low_value,
            'Close': c.close_value,
            'Volume': c.volume,
        })

    data_frame = pandas.DataFrame(data, index=index)
    data_frame.index.name = 'Date'

    return data_frame


def run() -> None:
    data_frame = create_data_frame_from_ddb(ChartType.BTC_JPY_ONE_HOUR)
    if not data_frame.empty:
        levels = detect_levels(data_frame)
        mplfinance.plot(data_frame, hlines=levels, type='candle', mav=(5, 14, 21), volume=True)


if __name__ == '__main__':
    run()
