import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.loader import load_prices

DEFAULT_CSV = Path(__file__).resolve().parent.parent / "data" / "market_data.csv"


@asynccontextmanager
async def lifespan(app: FastAPI):
    csv_path = os.environ.get("MARKET_DATA_CSV", DEFAULT_CSV)
    app.state.prices = load_prices(csv_path)
    yield


app = FastAPI(title="Instrument Price Dashboard API", lifespan=lifespan)


@app.get("/api/health")
def health():
    return {"status": "ok"}
