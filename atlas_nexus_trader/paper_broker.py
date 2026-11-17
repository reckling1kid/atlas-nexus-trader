from .models import Action, Candle, Trade


class PaperBroker:
    """Local simulated broker. No network or broker integration is performed."""

    def __init__(self, initial_cash: float):
        if initial_cash <= 0:
            raise ValueError("initial_cash must be positive")
        self.cash = initial_cash
        self.position_units = 0.0
        self.trades: list[Trade] = []

    def execute(self, symbol: str, action: Action, units: float, candle: Candle) -> Trade:
        if action not in (Action.BUY, Action.SELL):
            raise ValueError("paper broker only executes BUY or SELL")
        if units <= 0:
            raise ValueError("units must be positive")
        signed_units = units if action is Action.BUY else -units
        if self.position_units + signed_units < 0:
            raise ValueError("cannot sell more units than the paper position holds")
        amount = candle.close * units
        if action is Action.BUY and amount > self.cash:
            raise ValueError("insufficient paper cash")
        self.cash += -amount if action is Action.BUY else amount
        self.position_units += signed_units
        trade = Trade(candle.timestamp, symbol, action, units, candle.close, self.cash)
        self.trades.append(trade)
        return trade
