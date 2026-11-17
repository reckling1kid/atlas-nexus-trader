from datetime import datetime, timezone

import pytest

from atlas_nexus_trader.config import Settings
from atlas_nexus_trader.models import Action, Candle, Signal
from atlas_nexus_trader.paper_broker import PaperBroker
from atlas_nexus_trader.risk import RiskManager
from atlas_nexus_trader.signals import MovingAverageRsiStrategy


def candle(price: float) -> Candle:
    return Candle(datetime.now(timezone.utc), price, price + 1, price - 1, price)


def test_settings_default_to_paper_only():
    assert Settings().paper_trading is True


def test_strategy_holds_without_enough_data():
    assert MovingAverageRsiStrategy().generate([candle(100)]).action is Action.HOLD


def test_risk_blocks_hold_and_daily_loss_limit():
    manager = RiskManager(max_position_units=1, max_daily_loss=100)
    hold = manager.validate(Signal(Action.HOLD, "no signal"), 1, 0)
    loss = manager.validate(Signal(Action.BUY, "test"), 1, -100)
    assert not hold.allowed
    assert not loss.allowed


def test_paper_broker_updates_cash_and_position():
    broker = PaperBroker(initial_cash=1000)
    trade = broker.execute("DEMO", Action.BUY, 2, candle(100))
    assert broker.position_units == 2
    assert broker.cash == 800
    assert trade.price == 100


def test_paper_broker_rejects_oversell():
    broker = PaperBroker(initial_cash=1000)
    with pytest.raises(ValueError, match="cannot sell"):
        broker.execute("DEMO", Action.SELL, 1, candle(100))
