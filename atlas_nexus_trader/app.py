import logging
import os

from .backtest import run_backtest
from .config import Settings
from .csv_data import load_candles_csv
from .demo_data import make_demo_candles
from .models import Action
from .paper_broker import PaperBroker
from .risk import RiskManager
from .signals import MovingAverageRsiStrategy


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number") from exc


def run(settings: Settings | None = None) -> None:
    settings = settings or Settings.from_env()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger("atlas_nexus_trader")

    csv_path = os.getenv("ATLAS_CANDLES_CSV")
    if csv_path:
        candles = load_candles_csv(csv_path)
        data_source = f"CSV: {csv_path}"
    else:
        candles = make_demo_candles()
        data_source = "synthetic demo data"

    mode = os.getenv("ATLAS_MODE", "paper").strip().lower()
    if mode == "backtest":
        result = run_backtest(
            candles,
            initial_cash=settings.initial_cash,
            units=settings.max_position_units,
            max_daily_loss=settings.max_daily_loss,
            fee_bps=_env_float("ATLAS_BACKTEST_FEE_BPS", 0.0),
            slippage_bps=_env_float("ATLAS_BACKTEST_SLIPPAGE_BPS", 0.0),
        )
        logger.info("Mode: BACKTEST (paper simulation) | Symbol: %s | Candles: %s", settings.symbol, data_source)
        logger.info(
            "Final equity: %.2f | Return: %.2f%% | Max drawdown: %.2f%% | Fills: %d | Fees: %.2f",
            result.final_cash,
            result.total_return_pct,
            result.max_drawdown_pct,
            result.trade_count,
            result.fees_paid,
        )
        return
    if mode != "paper":
        raise ValueError("ATLAS_MODE must be 'paper' or 'backtest'")

    strategy = MovingAverageRsiStrategy()
    broker = PaperBroker(settings.initial_cash)
    risk = RiskManager(settings.max_position_units, settings.max_daily_loss)
    signal = strategy.generate(candles)
    latest = candles[-1]
    decision = risk.validate(signal, settings.max_position_units, daily_pnl=0.0)

    logger.info("Mode: PAPER SNAPSHOT | Symbol: %s | Candles: %s", settings.symbol, data_source)
    logger.info("Signal on supplied history: %s (%s)", signal.action.value, signal.reason)
    if decision.allowed:
        if signal.action is Action.SELL and broker.position_units < settings.max_position_units:
            logger.info("No paper position to sell; simulated sell skipped")
        else:
            try:
                trade = broker.execute(settings.symbol, signal.action, settings.max_position_units, latest)
            except ValueError as exc:
                logger.info("Paper execution rejected: %s", exc)
            else:
                logger.info("Illustrative simulated fill at final close: %s %.4f @ %.4f; paper cash %.2f", trade.action.value, trade.units, trade.price, trade.cash_after)
    else:
        logger.info("No trade: %s", decision.reason)
    logger.info("Paper position: %.4f units; paper cash: %.2f", broker.position_units, broker.cash)


def main() -> None:
    run()
