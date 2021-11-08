from typing import Dict, Union, List, Tuple

import pandas
import mplfinance
import time
import threading
from datetime import datetime, timezone

from pynamodb.exceptions import DoesNotExist

from libraries.exchanges.bitflyer import ProductCode, Candlestick, ChartType
from libraries.exchanges.bitflyer.models import TickerTable, ProductCodeIndex, ChartTable

STICK_OF = Dict[datetime, Dict[str, Union[int, float, datetime]]]
STICKS_OF = Dict[ChartType, STICK_OF]


def determine_period(ts: datetime, duration: int) -> datetime:
    if duration < Candlestick.ONE_MINUTE.value:
        second, _ = divmod(ts.second, duration)
        return datetime(ts.year, ts.month, ts.day, ts.hour, ts.minute, second * duration, tzinfo=timezone.utc)

    if duration < Candlestick.ONE_HOUR.value:
        duration, _ = divmod(duration, 60)
        minute, _ = divmod(ts.minute, duration)
        return datetime(ts.year, ts.month, ts.day, ts.hour, minute * duration, tzinfo=timezone.utc)

    if duration < Candlestick.ONE_DAY.value:
        duration, _ = divmod(duration, 60 * 60)
        hour, _ = divmod(ts.hour, duration)
        return datetime(ts.year, ts.month, ts.day, hour * duration, tzinfo=timezone.utc)

    if duration == Candlestick.ONE_DAY.value:
        return datetime(ts.year, ts.month, ts.day, tzinfo=timezone.utc)

    if duration == Candlestick.ONE_WEEK.value:
        cal = ts.isocalendar()
        return datetime.fromisocalendar(cal.year, cal.week, 1)

    raise RuntimeError(f'Unsupported timeframe: {duration}')


def summarize(stick_of: STICK_OF, duration: int) -> STICK_OF:
    new_stick_of: STICK_OF = {}

    for ts, stick in stick_of.items():
        period = determine_period(ts, duration)

        if period not in new_stick_of:
            new_stick_of[period] = {
                'high': stick['high'],
                'low': stick['low'],
                'open': stick['open'],
                'close': stick['close'],
                'volume': stick['volume'],
                'open_ts': stick['open_ts'],
                'close_ts': stick['close_ts'],
            }
            continue

        new_stick_of[period]['volume'] += stick['volume']
        new_stick_of[period]['high'] = max(new_stick_of[period]['high'], stick['high'])
        new_stick_of[period]['low'] = min(new_stick_of[period]['low'], stick['low'])
        if new_stick_of[period]['open_ts'] > stick['open_ts']:
            new_stick_of[period]['open_ts'] = stick['open_ts']
            new_stick_of[period]['open'] = stick['open']
        if new_stick_of[period]['close_ts'] < stick['close_ts']:
            new_stick_of[period]['close_ts'] = stick['close_ts']
            new_stick_of[period]['close'] = stick['close']

    return new_stick_of


def query_tickers(product_code: ProductCode) -> Tuple[List[TickerTable], STICK_OF]:
    _from = datetime(2021, 11, 4, tzinfo=timezone.utc)
    until = datetime(2030, 11, 5, 23, tzinfo=timezone.utc)
    result = ProductCodeIndex.query(
        product_code,
        ProductCodeIndex.timestamp.between(_from, until),
    )
    stick_of: STICK_OF = {}
    tickers = []

    for ticker in result:
        t: TickerTable = ticker
        tickers.append(t)
        ts: datetime = t.timestamp

        stick_of[ts] = {
            'high': t.ltp,
            'low': t.ltp,
            'open': t.ltp,
            'close': t.ltp,
            'volume': t.volume,
            'open_ts': ts,
            'close_ts': ts,
        }

    return tickers, stick_of


def store(sticks_of: STICKS_OF) -> None:
    with ChartTable.batch_write() as batch:
        for chart_type, stick_of in sticks_of.items():
            for ts, stick in stick_of.items():
                try:
                    chart = ChartTable.get(chart_type, ts)
                except DoesNotExist:
                    chart = ChartTable(chart_type, ts)

                chart.volume = (chart.volume or 0) + stick['volume']

                if chart.high_value is None or chart.high_value < stick['high']:
                    chart.high_value = stick['high']
                if chart.low_value is None or chart.low_value > stick['low']:
                    chart.low_value = stick['low']

                if chart.open_timestamp is None or chart.open_timestamp > stick['open_ts']:
                    chart.open_timestamp = stick['open_ts']
                    chart.open_value = stick['open']
                if chart.close_timestamp is None or chart.close_timestamp < stick['close_ts']:
                    chart.close_timestamp = stick['close_ts']
                    chart.close_value = stick['close']

                batch.save(chart)


def run(product_code: ProductCode) -> None:
    tickers, stick_of = query_tickers(product_code)
    sticks_of: STICKS_OF = {}

    for c in Candlestick:
        chart_type = getattr(ChartType, f'{product_code.name}_{c.name}')
        sticks_of[chart_type] = summarize(stick_of, c.value)
        stick_of = sticks_of[chart_type]

    store(sticks_of)

    with TickerTable.batch_write() as batch:
        for t in tickers:
            batch.delete(t)


if __name__ == '__main__':
    interval = 10
    start_time = time.time()

    def _run() -> None:
        run(ProductCode.BTC_JPY)
        run(ProductCode.FX_BTC_JPY)

    while True:
        t = threading.Thread(target=_run)
        t.start()
        t.join()

        time_to_wait = ((start_time - time.time()) % interval) or interval
        time.sleep(time_to_wait)
