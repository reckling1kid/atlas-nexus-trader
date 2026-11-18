from collections.abc import Sequence
from dataclasses import dataclass
import math
from statistics import pstdev

from .indicators import rsi, sma
from .models import Action, Candle, Signal


@dataclass(frozen=True)
class AgentAssessment:
    """One deterministic specialist's explainable assessment."""

    agent: str
    action: Action
    reason: str
    confidence: float
    veto: bool = False


@dataclass(frozen=True)
class MultiAgentAnalysis:
    signal: Signal
    assessments: tuple[AgentAssessment, ...]


class TrendAgent:
    name = "trend"

    def assess(self, candles: Sequence[Candle]) -> AgentAssessment:
        closes = [c.close for c in candles]
        fast, slow = sma(closes, 5), sma(closes, 12)
        if fast is None or slow is None:
            return _neutral(self.name, "Not enough bars for trend averages")
        if fast > slow:
            return AgentAssessment(self.name, Action.BUY, "5-bar average is above 12-bar average", 0.7)
        if fast < slow:
            return AgentAssessment(self.name, Action.SELL, "5-bar average is below 12-bar average", 0.7)
        return _neutral(self.name, "Trend averages are equal")


class MomentumAgent:
    name = "momentum"

    def assess(self, candles: Sequence[Candle]) -> AgentAssessment:
        momentum = rsi([c.close for c in candles], 7)
        if momentum is None:
            return _neutral(self.name, "Not enough bars for RSI")
        if 50 < momentum < 70:
            return AgentAssessment(self.name, Action.BUY, f"RSI momentum is positive ({momentum:.1f})", 0.65)
        if 30 < momentum < 50:
            return AgentAssessment(self.name, Action.SELL, f"RSI momentum is negative ({momentum:.1f})", 0.65)
        return _neutral(self.name, f"RSI is outside the directional range ({momentum:.1f})")


class GapAgent:
    name = "gap"

    def __init__(self, min_gap_bps: float = 10.0):
        if not math.isfinite(min_gap_bps) or min_gap_bps < 0:
            raise ValueError("min_gap_bps must be a non-negative finite number")
        self.min_gap_bps = min_gap_bps

    def assess(self, candles: Sequence[Candle]) -> AgentAssessment:
        if len(candles) < 2:
            return _neutral(self.name, "Not enough bars to assess an opening gap")
        previous_close = candles[-2].close
        gap_bps = (candles[-1].open / previous_close - 1) * 10_000
        if gap_bps >= self.min_gap_bps:
            return AgentAssessment(self.name, Action.BUY, f"Opening gap up ({gap_bps:.1f} bps)", 0.55)
        if gap_bps <= -self.min_gap_bps:
            return AgentAssessment(self.name, Action.SELL, f"Opening gap down ({gap_bps:.1f} bps)", 0.55)
        return _neutral(self.name, f"No material opening gap ({gap_bps:.1f} bps)")


class VolumeAgent:
    name = "volume"

    def assess(self, candles: Sequence[Candle]) -> AgentAssessment:
        if len(candles) < 2 or candles[-1].volume <= 0:
            return _neutral(self.name, "Current or prior volume is unavailable")
        baseline = [c.volume for c in candles[-21:-1] if c.volume > 0]
        if not baseline:
            return _neutral(self.name, "No positive historical volume baseline")
        average_volume = sum(baseline) / len(baseline)
        if candles[-1].volume < average_volume:
            return _neutral(self.name, "Current volume is below its historical baseline")
        if candles[-1].close > candles[-1].open:
            return AgentAssessment(self.name, Action.BUY, "Above-baseline volume on an up candle", 0.6)
        if candles[-1].close < candles[-1].open:
            return AgentAssessment(self.name, Action.SELL, "Above-baseline volume on a down candle", 0.6)
        return _neutral(self.name, "Above-baseline volume but no candle direction")


class VolatilityRiskAgent:
    name = "volatility_risk"

    def __init__(self, max_bar_volatility: float = 0.05):
        if not math.isfinite(max_bar_volatility) or max_bar_volatility <= 0:
            raise ValueError("max_bar_volatility must be a positive finite number")
        self.max_bar_volatility = max_bar_volatility

    def assess(self, candles: Sequence[Candle]) -> AgentAssessment:
        closes = [c.close for c in candles[-21:]]
        returns = [current / previous - 1 for previous, current in zip(closes, closes[1:])]
        if len(returns) < 2:
            return AgentAssessment(self.name, Action.HOLD, "Insufficient returns to estimate volatility", 1.0, veto=True)
        volatility = pstdev(returns)
        if volatility > self.max_bar_volatility:
            return AgentAssessment(
                self.name,
                Action.HOLD,
                f"Risk veto: per-bar return volatility {volatility:.2%} exceeds {self.max_bar_volatility:.2%}",
                1.0,
                veto=True,
            )
        return AgentAssessment(self.name, Action.HOLD, f"Volatility within configured threshold ({volatility:.2%})", 1.0)


class DecisionAgent:
    name = "decision"

    def assess(self, analysts: Sequence[AgentAssessment]) -> AgentAssessment:
        if any(assessment.veto for assessment in analysts):
            reasons = "; ".join(a.reason for a in analysts if a.veto)
            return AgentAssessment(self.name, Action.HOLD, reasons, 1.0)
        directional = [a for a in analysts if a.agent != VolatilityRiskAgent.name and a.action in (Action.BUY, Action.SELL)]
        buys = sum(a.action is Action.BUY for a in directional)
        sells = sum(a.action is Action.SELL for a in directional)
        required = 3
        if buys >= required and buys > sells:
            return AgentAssessment(self.name, Action.BUY, f"{buys} of {len(directional)} directional analysts support BUY", buys / max(len(directional), 1))
        if sells >= required and sells > buys:
            return AgentAssessment(self.name, Action.SELL, f"{sells} of {len(directional)} directional analysts support SELL", sells / max(len(directional), 1))
        return AgentAssessment(self.name, Action.HOLD, f"No 3-of-4 directional consensus (buy={buys}, sell={sells})", 0.0)


class MultiAgentStrategy:
    """Six deterministic cooperating agents; no LLM, network, or order access."""

    def __init__(self, *, min_gap_bps: float = 10.0, max_bar_volatility: float = 0.05):
        self.analysts = (
            TrendAgent(),
            MomentumAgent(),
            GapAgent(min_gap_bps),
            VolumeAgent(),
            VolatilityRiskAgent(max_bar_volatility),
        )
        self.decision_agent = DecisionAgent()

    def analyze(self, candles: Sequence[Candle]) -> MultiAgentAnalysis:
        assessments = tuple(agent.assess(candles) for agent in self.analysts)
        decision = self.decision_agent.assess(assessments)
        all_assessments = assessments + (decision,)
        return MultiAgentAnalysis(Signal(decision.action, decision.reason), all_assessments)

    def generate(self, candles: Sequence[Candle]) -> Signal:
        return self.analyze(candles).signal


def _neutral(agent: str, reason: str) -> AgentAssessment:
    return AgentAssessment(agent, Action.HOLD, reason, 0.0)
