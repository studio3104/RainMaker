import pandas
import mplfinance

from libraries.exchanges.bitflyer import ChartType
from libraries.exchanges.bitflyer.models import ChartTable
from libraries.signals.support_resistance import SupportResistance, Fractal, KMeans


def plot(_df: pandas.DataFrame, _sr: SupportResistance.__class__) -> None:
    sr: SupportResistance = _sr(_df)
    mplfinance.plot(
        _df, title=_sr.__name__, type='candle', mav=(5, 14, 21), volume=False,
        # hlines={
        #     'hlines': sr.levels + sr.supports + sr.resistances,
        #     'colors': ['b' for _ in sr.levels] + ['g' for _ in sr.supports] + ['r' for _ in sr.resistances],
        #     'linewidths': tuple([0.5 for _ in range(len(sr.levels) + len(sr.supports) + len(sr.resistances))]),
        #     'linestyle': '-.',
        # }
        hlines={
            'hlines': sr.levels,
            'linewidths': tuple([0.5 for _ in range(len(sr.levels))]),
            'linestyle': '-.',
        },
    )


if __name__ == '__main__':
    from datetime import datetime
    df = ChartTable.query_as_data_frame(
        ChartType.BTC_JPY_FIFTEEN_MINUTES,
        ChartTable.period_from.between(datetime(2021, 11, 8, 1), datetime(2021, 11, 8, 18, 30)))
    if df.empty:
        exit()

    plot(df, KMeans)
    plot(df, Fractal)
