"""API response models."""

import datetime as dt

from pydantic import BaseModel


class PricePoint(BaseModel):
    date: dt.date
    price: float


class PriceSeries(BaseModel):
    ticker: str
    prices: list[PricePoint]


class PriceStats(BaseModel):
    ticker: str
    start_date: dt.date
    end_date: dt.date
    first_price: float
    last_price: float
    total_return_pct: float
    daily_volatility_pct: float | None  # None when there are fewer than 3 prices
    max_drawdown_pct: float
