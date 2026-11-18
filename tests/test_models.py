from datetime import datetime, timezone

import pytest

from atlas_nexus_trader.models import Candle


def test_candle_rejects_non_finite_ohlcv_values():
    with pytest.raises(ValueError, match="finite"):
        Candle(datetime.now(timezone.utc), 10, float("inf"), 9, 10)
