import enum


class Candlestick(enum.Enum):
    FIFTEEN_SECONDS = 15
    THIRTY_SECONDS = 30

    ONE_MINUTE: int = 60
    FIVE_MINUTES = ONE_MINUTE * 5
    TEN_MINUTES = ONE_MINUTE * 10
    FIFTEEN_MINUTES = ONE_MINUTE * 15
    THIRTY_MINUTES = ONE_MINUTE * 30

    ONE_HOUR: int = ONE_MINUTE * 60
    FOUR_HOURS = ONE_HOUR * 4
    EIGHT_HOURS = ONE_HOUR * 8

    ONE_DAY: int = ONE_HOUR * 24
    ONE_WEEK = ONE_DAY * 7


class Channel(enum.Enum):
    pass


class PublicChannel(Channel):
    lightning_board_snapshot = enum.auto()
    lightning_board = enum.auto()
    lightning_ticker = enum.auto()
    lightning_executions = enum.auto()


class ProductCode(enum.Enum):
    BTC_JPY = enum.auto()
    XRP_JPY = enum.auto()
    ETH_JPY = enum.auto()
    XLM_JPY = enum.auto()
    MONA_JPY = enum.auto()
    ETH_BTC = enum.auto()
    BCH_BTC = enum.auto()
    FX_BTC_JPY = enum.auto()


class State(enum.Enum):
    RUNNING = enum.auto()
    CLOSED = enum.auto()
    STARTING = enum.auto()
    PREOPEN = enum.auto()
    CIRCUIT_BREAK = enum.auto()
    AWAITING_SQ = enum.auto()
    MATURED = enum.auto()


chart_types = []
for p in ProductCode:
    for c in Candlestick:
        chart_types.append((f'{p.name}_{c.name}', c.value))


ChartType = enum.Enum('ChartType', chart_types)
