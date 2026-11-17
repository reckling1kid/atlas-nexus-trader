import logging

from .config import Settings
from .demo_data import make_demo_candles
from .paper_broker import PaperBroker
from .risk import RiskManager
from .signals import MovingAverageRsiStrategy


def run(settings: Settings | None = None) -> None:
    settings = settings or Settings.from_env()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger("atlas_nexus_trader")

    # This first milestone intentionally uses generated demo candles and simulated fills.
    candles = make_demo_candles()
    strategy = MovingAverageRsiStrategy()
    broker = PaperBroker(settings.initial_cash)
    risk = RiskManager(settings.max_position_units, settings.max_daily_loss)
    signal = strategy.generate(candles)
    latest = candles[-1]
    decision = risk.validate(signal, settings.max_position_units, daily_pnl=0.0)

    logger.info("Mode: PAPER ONLY | Symbol: %s | Candles: synthetic demo data", settings.symbol)
    logger.info("Signal: %s (%s)", signal.action.value, signal.reason)
    if decision.allowed:
        trade = broker.execute(settings.symbol, signal.action, settings.max_position_units, latest)
        logger.info("Simulated fill: %s %.4f @ %.4f; paper cash %.2f", trade.action.value, trade.units, trade.price, trade.cash_after)
    else:
        logger.info("No trade: %s", decision.reason)
    logger.info("Paper position: %.4f units; paper cash: %.2f", broker.position_units, broker.cash)


def main() -> None:
    run()
