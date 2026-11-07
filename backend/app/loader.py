"""Load and validate the market data CSV."""

from __future__ import annotations

import csv
import math
from datetime import date
from pathlib import Path

from app.models import DailyPrice, PriceData, normalize_ticker

REQUIRED_COLUMNS = ("date", "ticker", "price")


class DataLoadError(ValueError):
    """Raised when the CSV is missing or malformed."""


def load_prices(path: str | Path) -> PriceData:
    """Read the CSV into {ticker: [DailyPrice, ...]} sorted by date.

    Raises DataLoadError on any bad row so the app fails fast at startup.
    """
    path = Path(path)
    if not path.is_file():
        raise DataLoadError(f"CSV file not found: {path}")

    by_ticker: dict[str, dict[date, float]] = {}

    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise DataLoadError(f"{path}: missing column(s): {', '.join(missing)}")

        for row in reader:
            line = reader.line_num
            ticker = normalize_ticker(row["ticker"] or "")
            if not ticker:
                raise DataLoadError(f"{path}:{line}: empty ticker")

            try:
                day = date.fromisoformat((row["date"] or "").strip())
            except ValueError:
                raise DataLoadError(f"{path}:{line}: invalid date {row['date']!r}") from None

            try:
                price = float(row["price"])
            except (TypeError, ValueError):
                raise DataLoadError(f"{path}:{line}: invalid price {row['price']!r}") from None
            if not math.isfinite(price) or price <= 0:
                raise DataLoadError(f"{path}:{line}: price must be a positive number, got {price}")

            by_date = by_ticker.setdefault(ticker, {})
            if day in by_date:
                raise DataLoadError(f"{path}:{line}: duplicate row for {ticker} on {day}")
            by_date[day] = price

    if not by_ticker:
        raise DataLoadError(f"{path}: no data rows")

    return {
        ticker: [DailyPrice(d, p) for d, p in sorted(by_date.items())]
        for ticker, by_date in by_ticker.items()
    }
