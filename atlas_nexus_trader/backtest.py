from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
import math

from .models import Action, Candle, Signal
from .signals import MovingAverageRsiStrategy


@dataclass(frozen=True)
class EquityPoint:
    timestamp: object
    equity: float


@dataclass(frozen=True)
class BacktestResult:
    initial_cash: float
    final_cash: float
    total_return_pct: float
    max_drawdown_pct: float
    trade_count: int
    fees_paid: float
    equity_curve: tuple[EquityPoint, ...]


def run_backtest(
    candles: Sequence[Candle],
    *,
    initial_cash: float = 10_000.0,
    units: float = 1.0,
    max_daily_loss: float = 500.0,
    fee_bps: float = 0.0,
    slippage_bps: float = 0.0,
    strategy: MovingAverageRsiStrategy | None = None,
) -> BacktestResult:
    """Replay completed candles, making decisions from prior bars only.

    Signals computed from bars before the current bar are executed at the
    current bar's open. Open positions are liquidated at the final close.
    Fees and adverse slippage are charged on every fill. This is a simple
    educational simulator, not a guarantee of real-world execution quality.
    """
    _positive_finite("initial_cash", initial_cash)
    _positive_finite("units", units)
    _positive_finite("max_daily_loss", max_daily_loss)
    _nonnegative_finite("fee_bps", fee_bps)
    _nonnegative_finite("slippage_bps", slippage_bps)
    if fee_bps >= 10_000 or slippage_bps >= 10_000:
        raise ValueError("fee_bps and slippage_bps must be less than 10000")
    if not candles:
        raise ValueError("at least one candle is required")

    strategy = strategy or MovingAverageRsiStrategy()
    cash = initial_cash
    position = 0.0
    fees_paid = 0.0
    trade_count = 0
    equity_curve: list[EquityPoint] = [EquityPoint(candles[0].timestamp, initial_cash)]
    peak_equity = initial_cash
    max_drawdown = 0.0
    current_day: date = candles[0].timestamp.date()
    day_start_equity = initial_cash
    fee_rate = fee_bps / 10_000
    slippage_rate = slippage_bps / 10_000

    for index in range(1, len(candles)):
        bar = candles[index]
        previous_bar = candles[index - 1]
        if bar.timestamp.date() != current_day:
            day_start_equity = cash + position * previous_bar.close
            current_day = bar.timestamp.date()

        open_equity = cash + position * bar.open
        daily_pnl = open_equity - day_start_equity
        signal = strategy.generate(candles[:index])

        if signal.action is Action.BUY and position == 0 and daily_pnl > -max_daily_loss:
            fill_price = bar.open * (1 + slippage_rate)
            notional = fill_price * units
            fee = notional * fee_rate
            total_cost = notional + fee
            if total_cost <= cash:
                cash -= total_cost
                position = units
                fees_paid += fee
                trade_count += 1
        elif signal.action is Action.SELL and position > 0:
            fill_price = bar.open * (1 - slippage_rate)
            notional = fill_price * position
            fee = notional * fee_rate
            cash += notional - fee
            position = 0.0
            fees_paid += fee
            trade_count += 1

        close_equity = cash + position * bar.close
        equity_curve.append(EquityPoint(bar.timestamp, close_equity))
        peak_equity = max(peak_equity, close_equity)
        if peak_equity > 0:
            max_drawdown = max(max_drawdown, (peak_equity - close_equity) / peak_equity)

    if position > 0:
        last_bar = candles[-1]
        fill_price = last_bar.close * (1 - slippage_rate)
        notional = fill_price * position
        fee = notional * fee_rate
        cash += notional - fee
        fees_paid += fee
        position = 0.0
        trade_count += 1
        equity_curve[-1] = EquityPoint(last_bar.timestamp, cash)
        peak_equity = max(peak_equity, cash)
        if peak_equity > 0:
            max_drawdown = max(max_drawdown, (peak_equity - cash) / peak_equity)

    return BacktestResult(
        initial_cash=initial_cash,
        final_cash=cash,
        total_return_pct=(cash / initial_cash - 1) * 100,
        max_drawdown_pct=max_drawdown * 100,
        trade_count=trade_count,
        fees_paid=fees_paid,
        equity_curve=tuple(equity_curve),
    )


def _positive_finite(name: str, value: float) -> None:
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a positive finite number")


def _nonnegative_finite(name: str, value: float) -> None:
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be a non-negative finite number")
