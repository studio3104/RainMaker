from typing import Dict, Union

import pandas
import mplfinance
from datetime import datetime, timezone

from libraries.exchanges.bitflyer import ProductCode, Candlestick, ChartType
from libraries.exchanges.bitflyer.models import TickerTable, ProductCodeIndex

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


def query_tickers(product_code: ProductCode) -> STICK_OF:
    _from = datetime(2021, 11, 4, 5, 15, tzinfo=timezone.utc)
    until = datetime(2021, 11, 4, 7, tzinfo=timezone.utc)
    tickers = ProductCodeIndex.query(
        product_code,
        ProductCodeIndex.timestamp.between(_from, until),
    )
    stick_of: STICK_OF = {}

    for ticker in tickers:
        t: TickerTable = ticker
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

    return stick_of


def plot(sticks_of: STICKS_OF, chart_type: ChartType) -> None:
    data_frame = pandas.DataFrame([
        {
            'Open': v['open'],
            'High': v['high'],
            'Low': v['low'],
            'Close': v['close'],
            'Volume': v['volume'],
        }
        for _, v in sticks_of[chart_type].items()
    ], index=list(sticks_of[chart_type].keys()))
    data_frame.index.name = 'Date'

    mplfinance.plot(data_frame, type='candle', mav=(5, 14, 25), volume=True)


def run() -> None:
    product_code = ProductCode.BTC_JPY
    stick_of: STICK_OF = query_tickers(product_code)
    sticks_of: STICKS_OF = {}

    for c in Candlestick:
        chart_type = getattr(ChartType, f'{product_code.name}_{c.name}')
        sticks_of[chart_type] = summarize(stick_of, c.value)
        stick_of = sticks_of[chart_type]

    for ct in sticks_of.keys():
        plot(sticks_of, ct)


if __name__ == '__main__':
    run()
