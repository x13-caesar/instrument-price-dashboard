"""Price statistics. Each function takes a price Series sorted by date."""

import pandas as pd


def total_return_pct(prices: pd.Series) -> float:
    """(last / first - 1) * 100."""
    return float((prices.iloc[-1] / prices.iloc[0] - 1) * 100)


def daily_volatility_pct(prices: pd.Series) -> float | None:
    """Sample standard deviation of simple daily returns, in percent (not annualized).

    Returns None when there are fewer than two returns to measure.
    """
    returns = prices.pct_change().dropna()
    if len(returns) < 2:
        return None
    return float(returns.std() * 100)  # pandas std uses ddof=1 (sample)


def max_drawdown_pct(prices: pd.Series) -> float:
    """Largest peak-to-trough decline, in percent. Always <= 0; 0.0 if prices never fall."""
    return float((prices / prices.cummax() - 1).min() * 100)
