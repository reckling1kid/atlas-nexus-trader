# Atlas Nexus Trader

A modular Python trading-bot starter built **paper-trading first**. This initial version uses deterministic demo candles and a local simulated broker; it does not connect to MetaTrader 5 or place real orders.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m atlas_nexus_trader
```

Run tests with `pytest`.

## Safety and scope

- Paper trading is the only execution mode in this starter.
- Demo candles are synthetic and do not represent market data.
- Signals and sample strategy are educational software, not financial advice or a claim of profitability.
- Do not add broker credentials or enable live execution without independent review, comprehensive testing, and explicit safeguards.

## Layout

```text
atlas_nexus_trader/
  __main__.py
  app.py
  config.py
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

1. Replace demo candles with a market-data adapter (read-only at first).
2. Add historical replay/backtesting with transaction costs and out-of-sample evaluation.
3. Persist positions and risk state, and add monitoring/alerts.
4. Keep execution paper-only until the full system has been reviewed and tested.
