# Atlas Nexus Trader

A modular Python trading-bot starter built **paper-trading first**. It supports deterministic synthetic demo candles by default and optional local CSV candles; execution is simulated locally and never connects to a broker or places real orders.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m atlas_nexus_trader
```

Run tests with `pytest`.

## CSV candle input

Set `ATLAS_CANDLES_CSV` to a local CSV file path to use historical candles instead of the synthetic demo series:

```bash
ATLAS_CANDLES_CSV=data/candles.csv python -m atlas_nexus_trader
```

The CSV must have a header with `timestamp,open,high,low,close`; `volume` is optional and defaults to `0`. Timestamps use ISO-8601 format (UTC `Z` is accepted), and rows must be in strictly increasing timestamp order. CSV data is read-only and does not connect to a market-data service. If the variable is unset, synthetic demo candles remain the default.

## Safety and scope

- Paper trading is the only execution mode in this starter.
- Synthetic demo candles are not market data. Historical CSV data may be stale or inaccurate.
- Signals and sample strategy are educational software, not financial advice or a claim of profitability.
- Do not add broker credentials or enable live execution without independent review, comprehensive testing, and explicit safeguards.

## Layout

```text
atlas_nexus_trader/
  __main__.py
  app.py
  config.py
  csv_data.py
  models.py
  indicators.py
  signals.py
  risk.py
  paper_broker.py
  demo_data.py
  storage.py
tests/
```

## Next steps

1. Add historical replay/backtesting with transaction costs and out-of-sample evaluation.
2. Persist positions and risk state, and add monitoring/alerts.
3. Keep execution paper-only until the full system has been reviewed and tested.
