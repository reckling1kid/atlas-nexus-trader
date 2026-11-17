from dataclasses import dataclass
from datetime import datetime
from enum import Enum


@dataclass(frozen=True)
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0

    def __post_init__(self) -> None:
        if min(self.open, self.high, self.low, self.close) <= 0:
            raise ValueError("OHLC prices must be positive")
        if self.high < max(self.open, self.close, self.low):
            raise ValueError("high must be at least every other OHLC value")
        if self.low > min(self.open, self.close, self.high):
            raise ValueError("low must be at most every other OHLC value")
        if self.volume < 0:
            raise ValueError("volume cannot be negative")


class Action(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass(frozen=True)
class Signal:
    action: Action
    reason: str


@dataclass(frozen=True)
class Trade:
    timestamp: datetime
    symbol: str
    action: Action
    units: float
    price: float
    cash_after: float
