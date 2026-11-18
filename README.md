# Atlas Nexus Trader

A paper-only trading research scaffold with deterministic specialist agents, local CSV input, and historical replay. It has **no broker connection and no live-order capability**. It is not a proven profitable strategy or investment service.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m atlas_nexus_trader
pytest
```

## Six cooperating analysis agents

The agents are deterministic Python components, not independent LLMs or autonomous traders. They share the same validated candle history, emit structured explanations, and cannot place orders:

1. **Trend** — compares short and longer simple moving averages.
2. **Momentum** — classifies RSI into directional/neutral ranges.
3. **Gap** — measures the latest open against the preceding close; it is a basic gap observation, not a standalone execution instruction.
4. **Volume** — checks current volume against prior positive-volume bars and candle direction.
5. **Volatility risk** — vetoes a directional decision when recent per-bar return volatility exceeds the configured threshold; vetoes also apply when there is too little history to estimate risk.
6. **Decision** — requires at least three of four directional analysts to agree and respects the risk veto; otherwise returns HOLD.

All thresholds are configurable in code/environment and are simple heuristics, not calibrated market models. Agreement is not proof of accuracy. The default `paper` mode prints each agent's assessment and places **no simulated or real order**.

## CSV candle input

Set `ATLAS_CANDLES_CSV` to a local CSV path. Required header columns are `timestamp,open,high,low,close`; `volume` is optional and defaults to zero. ISO-8601 timestamps (including UTC `Z`) must be strictly increasing. Data is read locally only.

```bash
ATLAS_CANDLES_CSV=data/candles.csv python -m atlas_nexus_trader
```

## Historical replay

Run the same multi-agent strategy over historical candles with next-bar-open fills:

```bash
ATLAS_MODE=backtest ATLAS_CANDLES_CSV=data/candles.csv \\
  ATLAS_BACKTEST_FEE_BPS=5 ATLAS_BACKTEST_SLIPPAGE_BPS=2 \\
  python -m atlas_nexus_trader
```

Replay applies configured fee and adverse slippage on fills, checks the daily loss threshold before new entries, marks equity each bar, and liquidates any open position at the last close. Costs default to zero in code; configure realistic costs. Results are highly sensitive to data quality, thresholds, costs, and sample selection. This basic simulator does not model spreads, market impact, partial fills, dividends, financing, taxes, corporate actions, borrow availability, or exchange calendars. It does not provide walk-forward validation, benchmark comparisons, or statistical significance testing. Validate on unseen data and use conservative assumptions; historical results do not predict future performance.

Settings:

- `ATLAS_MODE`: `paper` (default, analysis only) or `backtest`.
- `ATLAS_CANDLES_CSV`: optional local history; absent means synthetic demo data (not market data).
- `ATLAS_BACKTEST_FEE_BPS`, `ATLAS_BACKTEST_SLIPPAGE_BPS`: simulated per-fill costs in basis points.
- `ATLAS_MIN_GAP_BPS`: minimum opening gap for the gap agent (default 10).
- `ATLAS_MAX_BAR_VOLATILITY`: volatility veto threshold (default 0.05).

## Safety and product readiness

This is an experimental software scaffold, **not ready to sell or advertise as accurate, reliable, or profitable**. Before any commercial use, get qualified legal/compliance advice, use properly licensed reliable data, threat-model and security-review the application, add reproducible out-of-sample validation, benchmark/cost modeling, robust observability and operational controls, and obtain independent review. Paper results are not a guarantee. Never put credentials in the repository. Live trading is deliberately not implemented.

## Project layout

```text
atlas_nexus_trader/
  agents.py
  app.py
  backtest.py
  config.py
  csv_data.py
  demo_data.py
  indicators.py
  models.py
  paper_broker.py
  risk.py
  signals.py
  storage.py
tests/
```
