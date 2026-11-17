import sqlite3
from pathlib import Path

from .models import Trade


class TradeStore:
    """Minimal SQLite paper-trade history store."""

    def __init__(self, path: str | Path = "atlas_trades.sqlite3"):
        self.path = str(path)
        with self._connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    action TEXT NOT NULL,
                    units REAL NOT NULL,
                    price REAL NOT NULL,
                    cash_after REAL NOT NULL
                )
            """)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def save(self, trade: Trade) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO trades (timestamp, symbol, action, units, price, cash_after) VALUES (?, ?, ?, ?, ?, ?)",
                (trade.timestamp.isoformat(), trade.symbol, trade.action.value, trade.units, trade.price, trade.cash_after),
            )
