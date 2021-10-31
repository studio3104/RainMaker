import enum


class Pair(enum.Enum):
    BTC_JPY = enum.auto()
    XRP_JPY = enum.auto()
    ETH_JPY = enum.auto()
    XLM_JPY = enum.auto()
    MONA_JPY = enum.auto()
    ETH_BTC = enum.auto()
    BCH_BTC = enum.auto()


class State(enum.Enum):
    RUNNING = enum.auto()
    CLOSED = enum.auto()
    STARTING = enum.auto()
    PREOPEN = enum.auto()
    CIRCUIT_BREAK = enum.auto()
    AWAITING_SQ = enum.auto()
    MATURED = enum.auto()
