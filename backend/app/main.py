from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.backtest import router as backtest_router
from app.api.simulation import router as simulation_router
from app.api.stocks import router as stocks_router
from app.api.strategies import router as strategies_router
from app.api.ws import router as ws_router
from app.config import settings
from app.data.cache import CachedDataProvider
from app.data.registry import registry
from app.data.yahoo import YahooFinanceProvider
from app.db.engine import async_session


@asynccontextmanager
async def lifespan(app: FastAPI):
    yahoo = YahooFinanceProvider()
    cached = CachedDataProvider(yahoo, async_session)
    registry.register(cached, default=True)
    yield


app = FastAPI(title="HFT Trading Bot", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print(settings.cors_origin_list)
app.include_router(stocks_router)
app.include_router(strategies_router)
app.include_router(backtest_router)
app.include_router(simulation_router)
app.include_router(ws_router)


@app.get("/")
async def root():
    return {"status": "ok", "service": "HFT Trading Bot API"}


@app.get("/api/health")
async def health():
    return {"status": "ok"}
