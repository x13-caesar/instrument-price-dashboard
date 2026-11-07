# Instrument Price Dashboard

A small full-stack app for browsing 200 instruments, charting their prices over a 30-day window, and comparing up to three of them.

- **Backend:** Python 3.12+ with FastAPI. Loads the CSV into memory at startup.
- **Frontend:** React 18 + TypeScript (Vite), charts with Recharts.

## Features

- Search-as-you-type list of all 200 tickers.
- Price line chart for the selected ticker over the 30-day window.
- Total return, daily volatility and max drawdown shown next to the chart.
- Select 2–3 tickers to overlay them on one chart for comparison.
- Loading and error states for when the API is unreachable or a ticker is unknown.

## Project structure

```
backend/
  app/
    main.py      # app setup: loads the CSV at startup, CORS, routes
    loader.py    # reads and validates the CSV into one price series per ticker (pandas)
    stats.py     # total return, daily volatility, max drawdown
    models.py    # API response models (Pydantic)
    routes.py    # API endpoints
  data/market_data.csv
  tests/         # pytest: loader, stats, API
frontend/
  src/
    api.ts       # axios client and response types
    useAsync.ts  # shared loading / error / retry hook
    format.ts    # number and date formatting
    App.tsx      # selection state and page layout
    components/  # TickerPicker, PriceChart, StatsTable, Status
```

## Running locally

**Prerequisites:** Python 3.12+ and Node.js 20.19+ or 22.12+ (required by Vite).

### Backend (http://127.0.0.1:8000)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Interactive API docs are at http://127.0.0.1:8000/docs.
To load a different CSV, set `MARKET_DATA_CSV=/path/to/file.csv`.

### Frontend (http://localhost:5173)

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend calls `http://127.0.0.1:8000/api` by default; override with `VITE_API_URL`.
The backend's CORS settings allow requests only from `http://localhost:5173` and `http://127.0.0.1:5173`.

### Tests

```bash
cd backend
.venv/bin/pytest
```

The 38 tests cover CSV loading and validation, the stats calculations (checked against hand-computed values), and every endpoint, including 404s and CORS.

## API

| Method | Route | Returns |
|---|---|---|
| GET | `/api/instruments` | Sorted list of all 200 tickers |
| GET | `/api/prices/{ticker}` | The full 30-day series for one ticker: `{ticker, prices: [{date, price}]}`. Returns 404 if the ticker is unknown |
| GET | `/api/prices/{ticker}/stats` | `{ticker, start_date, end_date, first_price, last_price, total_return_pct, daily_volatility_pct, max_drawdown_pct}`. Returns 404 if the ticker is unknown |
| GET | `/api/health` | `{"status": "ok"}` |

Ticker lookup is case-insensitive (`tick0001` works). Unknown tickers return `404 {"detail": "Unknown ticker: X"}`.

Example:

```bash
$ curl http://127.0.0.1:8000/api/prices/TICK0001/stats
{"ticker":"TICK0001","start_date":"2026-06-23","end_date":"2026-08-03","first_price":190.34,"last_price":172.89,
 "total_return_pct":-9.1678,"daily_volatility_pct":1.5232,"max_drawdown_pct":-13.3849}
```

## Stats definitions

| Stat | Definition |
|---|---|
| **Total return %** | `(last price / first price − 1) × 100` |
| **Daily volatility %** | Sample standard deviation (n − 1) of simple daily returns `p[t] / p[t−1] − 1`, × 100. It is **not annualized**. It is `null` when there are fewer than 3 prices (fewer than 2 returns) |
| **Max drawdown %** | The largest peak-to-trough decline: the minimum of `(price / running peak − 1) × 100`. Reported as a value ≤ 0 (e.g. `-13.38`), and `0` if the price never falls |

All values are percentages, rounded to 4 decimals in the API response only.

## Design decisions

- **Python instead of C#.** The brief asks for a C# backend. I built it with Python + FastAPI instead, keeping the same endpoints and behavior.
- **In-memory data with pandas.** The CSV is read once at startup into one date-indexed price series per ticker. pandas keeps both the loading and the stats code short.
- **Fail fast on bad data.** The app refuses to start if the CSV has missing columns, unparseable dates or prices, blank values, or duplicate `(ticker, date)` rows.
- **Comparison uses % change.** With one ticker selected, the chart shows its closing price. With 2–3 tickers, it plots % change since the first day, so instruments at very different price levels (e.g. 60 vs 460) share one readable axis. The stats table still shows the actual first and last prices.
- **No batch endpoint.** For comparison, the frontend fetches each ticker's series and stats in parallel, so the backend keeps exactly the three endpoints from the brief.
- **Stable colors.** Each selected ticker keeps its color until it is removed, so removing one never repaints the others. The three series colors were checked for color-blind separation.
- **Unknown-ticker path.** Pressing Enter in the search box selects the first match. If nothing matches, the app asks the API for the typed ticker anyway, so the API's 404 is shown to the user as "Unknown ticker: X".

## Assumptions and limitations

- Prices are assumed to be positive. The loader does not reject zero or negative prices, and a zero price would make the return-based stats undefined.
- Daily returns are computed between consecutive rows (trading days), with no adjustment for gaps such as weekends.
- There is no automated frontend test suite. The UI was checked manually and with a headless-browser script during development.

## Use of AI coding assistants

This project was built with **Claude Code** (Anthropic) as a pair programmer. I set the requirements and made the design calls; the assistant drafted code, which I reviewed.

- **Planning:** it drafted the backend plan and checked the sample CSV for shape and data quality. I revised the module layout, chose pandas over plain Python, and dropped a repository layer the first draft had.
- **Backend:** it wrote the loader, stats, models and routes, plus the pytest suite. It cross-checked the stats against a separate plain-Python calculation.
- **Frontend:** it scaffolded the Vite app and wrote the components, the axios client and the styling. It verified the UI states (single ticker, comparison, unknown ticker, API unreachable, phone width) with a headless-Chrome script.
- **Docs:** it drafted this README.
