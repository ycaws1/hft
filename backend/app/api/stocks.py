from datetime import datetime

from fastapi import APIRouter, Query

from app.data.registry import registry
from app.models.domain import OHLCV, StockSearchResult

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


@router.get("/search", response_model=list[StockSearchResult])
async def search_stocks(q: str = Query(..., min_length=1)):
    provider = registry.get()
    return await provider.search_symbols(q)


@router.get("/{symbol}/history", response_model=list[OHLCV])
async def get_stock_history(
    symbol: str,
    start: str = Query(..., description="Start date YYYY-MM-DD"),
    end: str = Query(..., description="End date YYYY-MM-DD"),
    interval: str = Query("1d", description="Bar interval: 1m, 5m, 1h, 1d"),
):
    provider = registry.get()
    start_dt = datetime.strptime(start, "%Y-%m-%d")
    end_dt = datetime.strptime(end, "%Y-%m-%d")
    return await provider.get_historical(symbol, start_dt, end_dt, interval)
