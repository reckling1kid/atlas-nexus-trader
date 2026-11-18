import logging
import os

from .config import Settings
from .csv_data import load_candles_csv
from .demo_data import make_demo_candles
from .models import Action
from .paper_broker import PaperBroker
from .risk import RiskManager
from .signals import MovingAverageRsiStrategy


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

    strategy = MovingAverageRsiStrategy()
    broker = PaperBroker(settings.initial_cash)
    risk = RiskManager(settings.max_position_units, settings.max_daily_loss)
    signal = strategy.generate(candles)
    latest = candles[-1]
    decision = risk.validate(signal, settings.max_position_units, daily_pnl=0.0)

    logger.info("Mode: PAPER ONLY | Symbol: %s | Candles: %s", settings.symbol, data_source)
    logger.info("Signal: %s (%s)", signal.action.value, signal.reason)
    if decision.allowed:
        if signal.action is Action.SELL and broker.position_units < settings.max_position_units:
            logger.info("No paper position to sell; simulated sell skipped")
        else:
            try:
                trade = broker.execute(settings.symbol, signal.action, settings.max_position_units, latest)
            except ValueError as exc:
                logger.info("Paper execution rejected: %s", exc)
            else:
                logger.info("Simulated fill: %s %.4f @ %.4f; paper cash %.2f", trade.action.value, trade.units, trade.price, trade.cash_after)
    else:
        logger.info("No trade: %s", decision.reason)
    logger.info("Paper position: %.4f units; paper cash: %.2f", broker.position_units, broker.cash)


def main() -> None:
    run()
