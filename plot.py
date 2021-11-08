import mplfinance

from libraries.exchanges.bitflyer import ChartType
from libraries.exchanges.bitflyer.models import ChartTable
from libraries.signals.support_resistance import Fractal


def run() -> None:
    data_frame = ChartTable.query_as_data_frame(ChartType.BTC_JPY_ONE_HOUR)
    if not data_frame.empty:
        sr = Fractal(data_frame)
        mplfinance.plot(data_frame, hlines=sr.levels, type='candle', mav=(5, 14, 21), volume=True)


if __name__ == '__main__':
    run()
