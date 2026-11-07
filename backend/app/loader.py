"""Load the market data CSV into one date-indexed price series per ticker."""

from pathlib import Path

import pandas as pd

PriceData = dict[str, pd.Series]


def load_prices(path: str | Path) -> PriceData:
    """Return {ticker: price Series indexed by date, sorted ascending}.

    pandas raises FileNotFoundError / ValueError for a missing file, missing
    columns, or non-numeric prices; the checks below cover what it can't.
    """
    df = pd.read_csv(path, usecols=["date", "ticker", "price"], dtype={"price": float})
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    df["ticker"] = df["ticker"].str.strip().str.upper().replace("", pd.NA)

    if df.empty:
        raise ValueError(f"{path}: no data rows")
    if df.isna().any().any():
        raise ValueError(f"{path}: missing values in {df.columns[df.isna().any()].tolist()}")
    if df.duplicated(["ticker", "date"]).any():
        raise ValueError(f"{path}: duplicate (ticker, date) rows")

    return {
        ticker: group.set_index("date")["price"].sort_index()
        for ticker, group in df.groupby("ticker")
    }
