from datetime import datetime, timedelta, timezone

from atlas_nexus_trader.agents import MultiAgentStrategy
from atlas_nexus_trader.models import Action, Candle


def make_candles(closes, *, gap=0.0, volume=100.0):
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    candles = []
    for i, close in enumerate(closes):
        open_price = close if i else close
        if i == len(closes) - 1:
            open_price = closes[-2] * (1 + gap) if len(closes) > 1 else close
        candles.append(Candle(start + timedelta(minutes=i), open_price, max(open_price, close) * 1.01, min(open_price, close) * 0.99, close, volume))
    return candles


def test_multi_agent_strategy_has_six_named_assessments():
    analysis = MultiAgentStrategy().analyze(make_candles([100 + i for i in range(15)], gap=0.02))

    assert [item.agent for item in analysis.assessments] == [
        "trend", "momentum", "gap", "volume", "volatility_risk", "decision"
    ]
    assert analysis.signal.action in Action


def test_multi_agent_risk_veto_blocks_directional_consensus():
    closes = [100.0]
    for i in range(1, 16):
        closes.append(closes[-1] * (1.15 if i % 2 else 0.87))
    analysis = MultiAgentStrategy(max_bar_volatility=0.01).analyze(make_candles(closes))

    assert analysis.assessments[4].veto is True
    assert analysis.signal.action is Action.HOLD


def test_gap_agent_does_not_vote_without_material_gap():
    analysis = MultiAgentStrategy().analyze(make_candles([100 + i for i in range(15)]))

    assert analysis.assessments[2].action is Action.HOLD
