from dataclasses import dataclass
import os


def _float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number") from exc


@dataclass(frozen=True)
class Settings:
    """Validated runtime settings. Execution is intentionally paper-only."""

    symbol: str = "DEMO"
    initial_cash: float = 10_000.0
    max_position_units: float = 1.0
    max_daily_loss: float = 500.0
    paper_trading: bool = True

    @classmethod
    def from_env(cls) -> "Settings":
        settings = cls(
            symbol=os.getenv("ATLAS_SYMBOL", "DEMO"),
            initial_cash=_float_env("ATLAS_INITIAL_CASH", 10_000.0),
            max_position_units=_float_env("ATLAS_MAX_POSITION_UNITS", 1.0),
            max_daily_loss=_float_env("ATLAS_MAX_DAILY_LOSS", 500.0),
        )
        if settings.initial_cash <= 0:
            raise ValueError("ATLAS_INITIAL_CASH must be positive")
        if settings.max_position_units <= 0:
            raise ValueError("ATLAS_MAX_POSITION_UNITS must be positive")
        if settings.max_daily_loss <= 0:
            raise ValueError("ATLAS_MAX_DAILY_LOSS must be positive")
        return settings
