from datetime import datetime, timezone

import pytest

from atlas_nexus_trader.csv_data import load_candles_csv


def test_load_csv_candles_with_optional_volume(tmp_path):
    path = tmp_path / "candles.csv"
    path.write_text(
        "timestamp,open,high,low,close,volume\n"
        "2026-01-01T00:00:00Z,10,12,9,11,100\n"
        "2026-01-01T00:01:00Z,11,13,10,12,\n",
        encoding="utf-8",
    )

    candles = load_candles_csv(path)

    assert len(candles) == 2
    assert candles[0].timestamp == datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert candles[0].volume == 100
    assert candles[1].volume == 0


def test_load_csv_rejects_missing_columns(tmp_path):
    path = tmp_path / "candles.csv"
    path.write_text("timestamp,close\n2026-01-01T00:00:00,10\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing required columns"):
        load_candles_csv(path)


def test_load_csv_rejects_non_increasing_timestamps(tmp_path):
    path = tmp_path / "candles.csv"
    path.write_text(
        "timestamp,open,high,low,close\n"
        "2026-01-01T00:01:00Z,10,12,9,11\n"
        "2026-01-01T00:00:00Z,11,13,10,12\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="strictly increasing"):
        load_candles_csv(path)


def test_load_csv_rejects_non_finite_values(tmp_path):
    path = tmp_path / "candles.csv"
    path.write_text(
        "timestamp,open,high,low,close\n"
        "2026-01-01T00:00:00Z,10,nan,9,11\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="finite"):
        load_candles_csv(path)


def test_load_csv_rejects_rows_with_extra_columns(tmp_path):
    path = tmp_path / "candles.csv"
    path.write_text(
        "timestamp,open,high,low,close\n"
        "2026-01-01T00:00:00Z,10,12,9,11,unexpected\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="too many columns"):
        load_candles_csv(path)
