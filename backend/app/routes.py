from typing import Annotated

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Request

from app import stats
from app.loader import PriceData
from app.models import PricePoint, PriceSeries, PriceStats

router = APIRouter(prefix="/api")


def get_prices(request: Request) -> PriceData:
    return request.app.state.prices


Prices = Annotated[PriceData, Depends(get_prices)]


def _get_series(prices: PriceData, ticker: str) -> tuple[str, pd.Series]:
    """Case-insensitive lookup; 404 if the ticker is unknown."""
    key = ticker.strip().upper()
    if key not in prices:
        raise HTTPException(status_code=404, detail=f"Unknown ticker: {ticker}")
    return key, prices[key]


def _round(value: float | None) -> float | None:
    return None if value is None else round(value, 4)


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/instruments")
def list_instruments(prices: Prices) -> list[str]:
    return sorted(prices)


@router.get("/prices/{ticker}")
def get_price_series(ticker: str, prices: Prices) -> PriceSeries:
    key, series = _get_series(prices, ticker)
    return PriceSeries(
        ticker=key,
        prices=[PricePoint(date=d.date(), price=float(p)) for d, p in series.items()],
    )


@router.get("/prices/{ticker}/stats")
def get_price_stats(ticker: str, prices: Prices) -> PriceStats:
    key, series = _get_series(prices, ticker)
    return PriceStats(
        ticker=key,
        start_date=series.index[0].date(),
        end_date=series.index[-1].date(),
        first_price=float(series.iloc[0]),
        last_price=float(series.iloc[-1]),
        total_return_pct=_round(stats.total_return_pct(series)),
        daily_volatility_pct=_round(stats.daily_volatility_pct(series)),
        max_drawdown_pct=_round(stats.max_drawdown_pct(series)),
    )
