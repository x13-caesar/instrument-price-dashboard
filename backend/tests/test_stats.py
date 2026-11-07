import math

import pandas as pd
import pytest

from app.stats import daily_volatility_pct, max_drawdown_pct, total_return_pct


def series(*prices: float) -> pd.Series:
    return pd.Series(prices, index=pd.date_range("2026-01-01", periods=len(prices)))


# --- total return ---------------------------------------------------------


@pytest.mark.parametrize(
    ("prices", "expected"),
    [
        ((100, 110, 121), 21.0),          # rising
        ((100, 90, 81), -19.0),           # falling
        ((100, 120, 90, 108, 130), 30.0), # only first and last matter
        ((50, 50, 50), 0.0),              # flat
        ((42,), 0.0),                     # single price
    ],
)
def test_total_return(prices, expected):
    assert total_return_pct(series(*prices)) == pytest.approx(expected)


# --- daily volatility -----------------------------------------------------


def test_volatility_hand_computed():
    # returns +10%, -10% -> mean 0, sample variance (0.01 + 0.01) / 1 -> std sqrt(0.02)
    assert daily_volatility_pct(series(100, 110, 99)) == pytest.approx(math.sqrt(0.02) * 100)


def test_volatility_is_zero_for_constant_returns():
    assert daily_volatility_pct(series(100, 110, 121)) == pytest.approx(0.0)
    assert daily_volatility_pct(series(50, 50, 50)) == pytest.approx(0.0)


@pytest.mark.parametrize("prices", [(42,), (100, 110)])
def test_volatility_needs_at_least_two_returns(prices):
    assert daily_volatility_pct(series(*prices)) is None


# --- max drawdown ---------------------------------------------------------


@pytest.mark.parametrize(
    ("prices", "expected"),
    [
        ((100, 110, 121), 0.0),            # never falls
        ((50, 50, 50), 0.0),               # flat
        ((100, 90, 81), -19.0),            # falls all the way
        ((100, 120, 90, 108, 130), -25.0), # 120 -> 90, then recovers to a new high
        ((100, 80, 150, 135), -20.0),      # largest drop (-20%), not the latest (-10%)
        ((42,), 0.0),                      # single price
    ],
)
def test_max_drawdown(prices, expected):
    assert max_drawdown_pct(series(*prices)) == pytest.approx(expected)


# --- types and real data --------------------------------------------------


def test_results_are_plain_python_floats():
    s = series(100, 120, 90, 108)
    for value in (total_return_pct(s), daily_volatility_pct(s), max_drawdown_pct(s)):
        assert type(value) is float


def test_against_sample_csv():
    from app.loader import load_prices
    from app.main import DEFAULT_CSV

    prices = load_prices(DEFAULT_CSV)["TICK0001"]
    assert total_return_pct(prices) == pytest.approx((172.89 / 190.34 - 1) * 100)
    assert max_drawdown_pct(prices) <= 0
    assert daily_volatility_pct(prices) > 0
