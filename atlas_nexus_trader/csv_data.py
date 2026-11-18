import csv
from datetime import datetime
from pathlib import Path

from .models import Candle


_REQUIRED_COLUMNS = ("timestamp", "open", "high", "low", "close")


def load_candles_csv(path: str | Path) -> list[Candle]:
    """Load timestamped OHLCV candles from a local CSV file.

    Required headers: timestamp,open,high,low,close. Volume is optional and
    defaults to zero. Timestamps must be ISO-8601; timezone-aware values are
    recommended. Rows are returned in file order and must be chronologically
    increasing.
    """
    csv_path = Path(path)
    try:
        handle = csv_path.open("r", newline="", encoding="utf-8-sig")
    except OSError as exc:
        raise ValueError(f"cannot read candle CSV {csv_path}: {exc}") from exc

    with handle:
        reader = csv.DictReader(handle, strict=True)
        if reader.fieldnames is None:
            raise ValueError("CSV is empty or missing a header row")
        headers = [header.strip().lower() for header in reader.fieldnames if header]
        if len(headers) != len(reader.fieldnames):
            raise ValueError("CSV contains an empty column name")
        if len(set(headers)) != len(headers):
            raise ValueError("CSV contains duplicate column names")
        missing = [column for column in _REQUIRED_COLUMNS if column not in headers]
        if missing:
            raise ValueError(f"CSV missing required columns: {', '.join(missing)}")

        reader.fieldnames = headers
        candles: list[Candle] = []
        previous_timestamp: datetime | None = None
        try:
            for row_number, row in enumerate(reader, start=2):
                if None in row:
                    raise ValueError(f"row {row_number}: too many columns")
                if all(value is None or not value.strip() for value in row.values()):
                    continue
                if any(row.get(column) is None or not row[column].strip() for column in _REQUIRED_COLUMNS):
                    raise ValueError(f"row {row_number}: missing required value")
                try:
                    timestamp_text = row["timestamp"].strip()
                    timestamp = datetime.fromisoformat(timestamp_text.replace("Z", "+00:00"))
                    values = {column: float(row[column]) for column in ("open", "high", "low", "close")}
                    volume_text = row.get("volume")
                    volume = float(volume_text) if volume_text and volume_text.strip() else 0.0
                    candle = Candle(timestamp=timestamp, **values, volume=volume)
                except (ValueError, TypeError) as exc:
                    raise ValueError(f"row {row_number}: invalid candle data: {exc}") from exc
                if previous_timestamp is not None:
                    if (timestamp.tzinfo is None) != (previous_timestamp.tzinfo is None):
                        raise ValueError(f"row {row_number}: timestamps must use a consistent timezone")
                    if timestamp <= previous_timestamp:
                        raise ValueError(f"row {row_number}: timestamps must be strictly increasing")
                candles.append(candle)
                previous_timestamp = timestamp
        except csv.Error as exc:
            raise ValueError(f"invalid CSV format: {exc}") from exc

    if not candles:
        raise ValueError("CSV contains no candle rows")
    return candles
