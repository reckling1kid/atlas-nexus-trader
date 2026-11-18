from datetime import datetime, timezone

import pytest

from atlas_nexus_trader.backtest import run_backtest
from atlas_nexus_trader.models import Candle, Signal, Action


def test_backtest_rejects_unsorted_candles():
    a = Candle(datetime(2026, 1, 2, tzinfo=timezone.utc), 10, 11, 9, 10)
    b = Candle(datetime(2026, 1, 1, tzinfo=timezone.utc), 10, 11, 9, 10)
    with pytest.raises(ValueError, match="strictly increasing"):
        run_backtest([a, b])


def test_backtest_rejects_mixed_naive_and_aware_timestamps():
    aware = Candle(datetime(2026, 1, 1, tzinfo=timezone.utc), 10, 11, 9, 10)
    naive = Candle(datetime(2026, 1, 1, 0, 1), 10, 11, 9, 10)
    with pytest.raises(ValueError, match="consistent timezone"):
        run_backtest([aware, naive])


class HoldStrategy:
    def generate(self, candles):
        return Signal(Action.HOLD, "test")


def test_backtest_hold_result_has_no_fills():
    candle = Candle(datetime(2026, 1, 1, tzinfo=timezone.utc), 10, 11, 9, 10)
    result = run_backtest([candle], strategy=HoldStrategy())
    assert result.trade_count == 0
    assert result.final_cash == result.initial_cash
