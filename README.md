# Atlas Nexus Trader

A modular Python trading-bot starter built **paper-trading first**. It supports deterministic synthetic demo candles by default and optional local CSV candles; it never connects to a broker or places real orders.

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

Set `ATLAS_CANDLES_CSV` to a local CSV path to load candles instead of the synthetic demo series:

```bash
ATLAS_CANDLES_CSV=data/candles.csv python -m atlas_nexus_trader
```

The CSV must have a header with `timestamp,open,high,low,close`; `volume` is optional and defaults to `0`. Timestamps use ISO-8601 format (`Z` is accepted), and rows must be in strictly increasing order. The loader validates OHLCV values and reads only local files; it does not fetch market data.

## Historical backtest

Set `ATLAS_MODE=backtest` to replay the loaded candles. The strategy sees only bars before the current one, and signals execute at the next bar's open. Any remaining position is liquidated at the final close. Optional cost settings are in basis points:

```bash
ATLAS_MODE=backtest ATLAS_CANDLES_CSV=data/candles.csv \\
  ATLAS_BACKTEST_FEE_BPS=5 ATLAS_BACKTEST_SLIPPAGE_BPS=2 \\
  python -m atlas_nexus_trader
```

The output reports ending cash after liquidation, total return, maximum drawdown, fill count, and fees. The default cost assumptions are zero, so specify realistic fees and slippage for evaluation. This small simulator does not model spreads, market impact, partial fills, dividends, or taxes; it is educational and is not evidence of a profitable strategy. Synthetic demo candles are not market data, and historical CSV data may be stale or inaccurate.

## Modes and safety

- Default `ATLAS_MODE=paper` is a one-shot **paper snapshot**, not a continuously running trading system. It evaluates the supplied history and illustrates a simulated fill at the final close; it should not be used to infer a deployable live signal.
- `ATLAS_MODE=backtest` is historical replay only. Both modes are paper-only and have no broker integration.
- Signals and sample strategy are educational software, not financial advice or a claim of profitability.
- Do not add broker credentials or enable live execution without independent review, comprehensive testing, and explicit safeguards.

## Layout

```text
atlas_nexus_trader/
  __main__.py
  app.py
  backtest.py
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

1. Add robust reporting for benchmark comparison and out-of-sample evaluation.
2. Persist positions and risk state, and add monitoring/alerts.
3. Keep execution paper-only until the full system has been reviewed and tested.
