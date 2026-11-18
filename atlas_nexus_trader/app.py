import logging
import os

from .agents import MultiAgentStrategy
from .backtest import run_backtest
from .config import Settings
from .csv_data import load_candles_csv
from .demo_data import make_demo_candles


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

    strategy = MultiAgentStrategy(
        min_gap_bps=_env_float("ATLAS_MIN_GAP_BPS", 10.0),
        max_bar_volatility=_env_float("ATLAS_MAX_BAR_VOLATILITY", 0.05),
    )
    mode = os.getenv("ATLAS_MODE", "paper").strip().lower()
    if mode == "backtest":
        result = run_backtest(
            candles,
            initial_cash=settings.initial_cash,
            units=settings.max_position_units,
            max_daily_loss=settings.max_daily_loss,
            fee_bps=_env_float("ATLAS_BACKTEST_FEE_BPS", 0.0),
            slippage_bps=_env_float("ATLAS_BACKTEST_SLIPPAGE_BPS", 0.0),
            strategy=strategy,
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

    analysis = strategy.analyze(candles)
    logger.info("Mode: PAPER ANALYSIS ONLY | Symbol: %s | Candles: %s", settings.symbol, data_source)
    for assessment in analysis.assessments:
        logger.info("Agent %s: %s (confidence %.0f%%) — %s", assessment.agent, assessment.action.value, assessment.confidence * 100, assessment.reason)
    logger.info("Consensus: %s (%s). No order was placed.", analysis.signal.action.value, analysis.signal.reason)
    logger.info("Historical dataset bars: %d; minimum for all agents is 12", len(candles))


def main() -> None:
    run()
