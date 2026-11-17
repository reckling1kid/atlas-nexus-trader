from datetime import datetime, timedelta, timezone
import random

from .models import Candle


def make_demo_candles(count: int = 40, seed: int = 7) -> list[Candle]:
    """Create repeatable synthetic candles for a smoke test; not market data."""
    if count <= 0:
        raise ValueError("count must be positive")
    rng = random.Random(seed)
    price = 100.0
    candles = []
    start = datetime.now(timezone.utc) - timedelta(minutes=count)
    for index in range(count):
        price = max(1.0, price + rng.uniform(-1.2, 1.2))
        spread = rng.uniform(0.05, 0.6)
        candles.append(Candle(
            timestamp=start + timedelta(minutes=index),
            open=price,
            high=price + spread,
            low=max(0.01, price - spread),
            close=price,
            volume=rng.uniform(10, 1000),
        ))
    return candles
