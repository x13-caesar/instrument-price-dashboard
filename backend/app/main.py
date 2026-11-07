import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.loader import load_prices
from app.routes import router

DEFAULT_CSV = Path(__file__).resolve().parent.parent / "data" / "market_data.csv"

# frontend dev server
FRONTEND_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    csv_path = os.environ.get("MARKET_DATA_CSV", DEFAULT_CSV)
    app.state.prices = load_prices(csv_path)
    yield


app = FastAPI(title="Instrument Price Dashboard API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_methods=["GET"],
    allow_headers=["*"],
)
app.include_router(router)
