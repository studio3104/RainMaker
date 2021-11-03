import json
from matplotlib import pyplot


def run() -> None:
    ticker_timestamps = []
    ltps = []
    rsis = []
    tickers = [[]]
    idx = 0

    with open('ticker1.log') as f:
        for i, line in enumerate(f):
            if i == 6274:
                idx += 1
                tickers.append([])
                continue
            if 6274 < i < 6697:
                continue

            _line = line.replace("'", '"')
            _line = _line.replace('None', 'null')
            r = json.loads(_line)

            tickers[idx].append({'timestamp': r['timestamp'], 'price': r['ltp']})

            ticker_timestamps.append(r['timestamp'])
            ltps.append(r['ltp'])
            rsis.append(r['rsi'])

    for i, t in enumerate(tickers):
        with open(f'tickers/ticker{str(i).zfill(4)}.json', mode='w') as f:
            f.write(json.dumps(t))

    return

    tx_timestamps = [ticker_timestamps[0]]
    bought = [[], []]
    sold = [[], []]
    profits = [0]
    with open('transaction.log') as f:
        for i, line in enumerate(f):
            _line = line.replace("'", '"')
            _line = _line.replace('None', 'null')
            r = json.loads(_line)

            if r['timestamp'] > ticker_timestamps[-1]:
                break

            if r['lossCutRate'] != 0.3:
                continue

            if r['action'] == 'SELL':
                tx_timestamps.append(r['timestamp'])
                profits.append(r['profit'])
            target = bought if r['action'] == 'BUY' else sold
            target[0].append(r['timestamp'])
            target[1].append(r['price'])
    tx_timestamps.append(ticker_timestamps[-1])
    profits.append(profits[-1])

    fig, (ax1, ax2, ax3) = pyplot.subplots(3, 1, gridspec_kw={'height_ratios': [3, 1, 1]})

    ax1.set_title('Ticker')
    ax1.plot(ticker_timestamps, ltps, color='gray')
    ax1.scatter(bought[0], bought[1], color='red')
    ax1.scatter(sold[0], sold[1], color='green')

    ax2.set_title('RSI')
    ax2.plot(ticker_timestamps, rsis)

    ax3.set_title('Profit')
    ax3.plot(tx_timestamps, profits)

    fig.tight_layout()
    pyplot.show()


if __name__ == '__main__':
    run()
