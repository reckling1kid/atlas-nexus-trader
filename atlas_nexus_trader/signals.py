from collections.abc import Sequence

from .indicators import rsi, sma
from .models import Action, Candle, Signal


class MovingAverageRsiStrategy:
    """Small illustrative strategy; it is not evidence of a profitable edge."""

    def __init__(self, fast_period: int = 5, slow_period: int = 12, rsi_period: int = 7):
        if fast_period <= 0 or slow_period <= fast_period or rsi_period <= 0:
            raise ValueError("periods must be positive and slow_period > fast_period")
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.rsi_period = rsi_period

    def generate(self, candles: Sequence[Candle]) -> Signal:
        closes = [candle.close for candle in candles]
        fast = sma(closes, self.fast_period)
        slow = sma(closes, self.slow_period)
        momentum = rsi(closes, self.rsi_period)
        if fast is None or slow is None or momentum is None:
            return Signal(Action.HOLD, "Not enough candle history")
        if fast > slow and momentum < 70:
            return Signal(Action.BUY, "Fast average above slow average; RSI below 70")
        if fast < slow and momentum > 30:
            return Signal(Action.SELL, "Fast average below slow average; RSI above 30")
        return Signal(Action.HOLD, "Strategy conditions not met")
