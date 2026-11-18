from datetime import datetime, timezone

import pytest

from atlas_nexus_trader.backtest import run_backtest
from atlas_nexus_trader.models import Action, Candle, Signal


class TwoStepStrategy:
    def generate(self, candles):
        if len(candles) == 1:
            return Signal(Action.BUY, "test entry")
        return Signal(Action.SELL, "test exit")


def candle(timestamp: str, open_price: float, close_price: float) -> Candle:
    parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    return Candle(parsed, open_price, max(open_price, close_price), min(open_price, close_price), close_price)


def test_backtest_uses_prior_bars_and_next_open_with_costs():
    candles = [
        candle("2026-01-01T00:00:00Z", 10, 10),
        candle("2026-01-01T00:01:00Z", 10, 11),
        candle("2026-01-01T00:02:00Z", 12, 12),
    ]

    result = run_backtest(
        candles,
        initial_cash=1_000,
        units=2,
        fee_bps=10,
        slippage_bps=100,
        strategy=TwoStepStrategy(),
    )

    assert result.trade_count == 2
    assert result.final_cash == pytest.approx(1_003.51604)
    assert result.fees_paid == pytest.approx(0.04396)
    assert result.equity_curve[1].equity == pytest.approx(1_001.7798)


def test_backtest_rejects_invalid_costs_and_empty_history():
    with pytest.raises(ValueError, match="at least one candle"):
        run_backtest([])
    with pytest.raises(ValueError, match="fee_bps"):
        run_backtest([candle("2026-01-01T00:00:00Z", 10, 10)], fee_bps=float("nan"))


def test_backtest_liquidates_open_position_at_last_close():
    candles = [
        candle("2026-01-01T00:00:00Z", 10, 10),
        candle("2026-01-01T00:01:00Z", 10, 12),
    ]

    class BuyAndHold:
        def generate(self, candles):
            return Signal(Action.BUY, "buy")

    result = run_backtest(candles, initial_cash=100, units=1, strategy=BuyAndHold())

    assert result.trade_count == 2
    assert result.final_cash == 102


def test_backtest_result_starts_with_initial_equity():
    candles = [candle("2026-01-01T00:00:00Z", 10, 10)]
    result = run_backtest(candles, initial_cash=100, strategy=TwoStepStrategy())

    assert result.equity_curve[0].equity == 100
    assert result.final_cash == 100
