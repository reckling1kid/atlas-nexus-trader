from dataclasses import dataclass

from .models import Action, Signal


@dataclass(frozen=True)
class RiskDecision:
    allowed: bool
    reason: str


class RiskManager:
    def __init__(self, max_position_units: float, max_daily_loss: float):
        if max_position_units <= 0 or max_daily_loss <= 0:
            raise ValueError("risk limits must be positive")
        self.max_position_units = max_position_units
        self.max_daily_loss = max_daily_loss

    def validate(self, signal: Signal, requested_units: float, daily_pnl: float) -> RiskDecision:
        if signal.action is Action.HOLD:
            return RiskDecision(False, "No trade: signal is HOLD")
        if requested_units <= 0 or requested_units > self.max_position_units:
            return RiskDecision(False, "Requested size is outside configured position limit")
        if daily_pnl <= -self.max_daily_loss:
            return RiskDecision(False, "Daily loss limit reached")
        return RiskDecision(True, "Paper trade passed configured risk checks")
