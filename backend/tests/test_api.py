import statistics

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routes import get_prices


@pytest.fixture
def client():
    """Client backed by the real CSV (loaded via the app's lifespan)."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def fake_client():
    """Client backed by a tiny hand-written dataset with easy-to-check stats."""

    def series(*prices: float) -> pd.Series:
        return pd.Series(prices, index=pd.date_range("2026-01-05", periods=len(prices)))

    fake = {
        "AAA": series(100, 120, 90, 108, 130),
        "BBB": series(50, 55),
    }
    app.dependency_overrides[get_prices] = lambda: fake
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.clear()


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


# --- /api/instruments -----------------------------------------------------


def test_instruments_lists_all_200_sorted(client):
    res = client.get("/api/instruments")
    assert res.status_code == 200
    tickers = res.json()
    assert len(tickers) == 200
    assert tickers == sorted(tickers)
    assert tickers[0] == "TICK0001" and tickers[-1] == "TICK0200"


# --- /api/prices/{ticker} -------------------------------------------------


def test_price_series(client):
    body = client.get("/api/prices/TICK0001").json()
    assert body["ticker"] == "TICK0001"
    points = body["prices"]
    assert len(points) == 30
    assert points[0] == {"date": "2026-06-23", "price": 190.34}
    assert points[-1] == {"date": "2026-08-03", "price": 172.89}
    dates = [p["date"] for p in points]
    assert dates == sorted(dates)


def test_ticker_lookup_is_case_insensitive(client):
    res = client.get("/api/prices/tick0001")
    assert res.status_code == 200
    assert res.json()["ticker"] == "TICK0001"


@pytest.mark.parametrize("path", ["/api/prices/NOPE", "/api/prices/NOPE/stats"])
def test_unknown_ticker_is_404(client, path):
    res = client.get(path)
    assert res.status_code == 404
    assert res.json() == {"detail": "Unknown ticker: NOPE"}


# --- /api/prices/{ticker}/stats -------------------------------------------


def test_stats_on_hand_written_data(fake_client):
    body = fake_client.get("/api/prices/aaa/stats").json()
    returns = [120 / 100 - 1, 90 / 120 - 1, 108 / 90 - 1, 130 / 108 - 1]
    assert body == {
        "ticker": "AAA",
        "start_date": "2026-01-05",
        "end_date": "2026-01-09",
        "first_price": 100.0,
        "last_price": 130.0,
        "total_return_pct": 30.0,
        "daily_volatility_pct": round(statistics.stdev(returns) * 100, 4),
        "max_drawdown_pct": -25.0,
    }


def test_volatility_is_null_with_too_few_prices(fake_client):
    body = fake_client.get("/api/prices/BBB/stats").json()
    assert body["daily_volatility_pct"] is None
    assert body["total_return_pct"] == 10.0


def test_stats_on_sample_csv(client):
    body = client.get("/api/prices/TICK0001/stats").json()
    assert body["start_date"] == "2026-06-23"
    assert body["end_date"] == "2026-08-03"
    assert body["total_return_pct"] == -9.1678
    assert body["daily_volatility_pct"] == 1.5232
    assert body["max_drawdown_pct"] == -13.3849


# --- CORS -----------------------------------------------------------------


def test_cors_allows_frontend_dev_server(client):
    res = client.get("/api/instruments", headers={"Origin": "http://localhost:5173"})
    assert res.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_rejects_other_origins(client):
    res = client.get("/api/instruments", headers={"Origin": "http://evil.example"})
    assert "access-control-allow-origin" not in res.headers
