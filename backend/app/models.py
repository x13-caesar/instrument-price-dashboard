"""Data types shared by the loader, stats and routes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class DailyPrice:
    date: date
    price: float


# Ticker -> price series sorted by date.
PriceData = dict[str, list[DailyPrice]]


def normalize_ticker(ticker: str) -> str:
    return ticker.strip().upper()
