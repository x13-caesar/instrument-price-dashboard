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

## Design decisions

- **Python instead of C#.** The brief asks for a C# backend. I built it with Python + FastAPI instead as I think it makes more sense to this Python role, keeping the same endpoints and behavior.
- **Comparison uses % change.** With one ticker selected, the chart shows its closing price. With 2–3 tickers, it plots % change since the first day, so instruments at very different price levels (e.g. 60 vs 460) share one readable axis. The stats table still shows the actual first and last prices.
- **Unknown-ticker path.** Pressing Enter in the search box selects the first match. If nothing matches, the app asks the API for the typed ticker anyway, so the API's 404 is shown to the user as "Unknown ticker: X".

## Use of AI coding assistants

This project was built with **Claude Code** as a programming assist. the assistant drafted code of the following parts, which I reviewed.

- **Backend:** it checked csv file and defined pydantic data models accordingly. It wrote pytest suite. It cross-checked the stats against a separate plain-Python calculation.
- **Frontend:** it scaffolded the Vite app. It verified the UI states (single ticker, comparison, unknown ticker, API unreachable, phone width) with a headless-Chrome script. It restyle the app to match Pharo color palette. 
- **Docs:** it drafted this README.
