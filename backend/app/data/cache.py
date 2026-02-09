from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.provider import DataProvider
from app.models.db_models import StockDataCache
from app.models.domain import OHLCV, StockSearchResult


class CachedDataProvider(DataProvider):
    """Wraps any DataProvider with PostgreSQL-backed caching for historical data."""

    def __init__(self, provider: DataProvider, session_factory):
        self._provider = provider
        self._session_factory = session_factory

    @property
    def name(self) -> str:
        return f"cached_{self._provider.name}"

    async def get_historical(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        interval: str = "1d",
    ) -> list[OHLCV]:
        # Ensure start/end are timezone-aware for comparison with DB timestamps
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)

        async with self._session_factory() as session:
            cached = await self._get_cached(session, symbol, start, end, interval)

            if cached:
                cached_start = min(b.timestamp for b in cached)
                cached_end = max(b.timestamp for b in cached)
                # Normalize for comparison
                cs = cached_start.replace(tzinfo=timezone.utc) if cached_start.tzinfo is None else cached_start
                ce = cached_end.replace(tzinfo=timezone.utc) if cached_end.tzinfo is None else cached_end
                if cs <= start and ce >= end:
                    return [b for b in cached if start <= (b.timestamp.replace(tzinfo=timezone.utc) if b.timestamp.tzinfo is None else b.timestamp) <= end]

            fresh = await self._provider.get_historical(symbol, start, end, interval)

            if fresh:
                await self._store_bars(session, symbol, interval, fresh)

            return fresh

    async def get_latest_price(self, symbol: str) -> float:
        return await self._provider.get_latest_price(symbol)

    async def search_symbols(self, query: str) -> list[StockSearchResult]:
        return await self._provider.search_symbols(query)

    async def _get_cached(
        self,
        session: AsyncSession,
        symbol: str,
        start: datetime,
        end: datetime,
        interval: str,
    ) -> list[OHLCV]:
        stmt = (
            select(StockDataCache)
            .where(
                StockDataCache.symbol == symbol,
                StockDataCache.interval == interval,
                StockDataCache.timestamp >= start,
                StockDataCache.timestamp <= end,
            )
            .order_by(StockDataCache.timestamp)
        )
        result = await session.execute(stmt)
        rows = result.scalars().all()
        return [
            OHLCV(
                timestamp=row.timestamp,
                open=float(row.open),
                high=float(row.high),
                low=float(row.low),
                close=float(row.close),
                volume=int(row.volume),
            )
            for row in rows
        ]

    async def _store_bars(
        self,
        session: AsyncSession,
        symbol: str,
        interval: str,
        bars: list[OHLCV],
    ) -> None:
        for bar in bars:
            stmt = (
                insert(StockDataCache)
                .values(
                    symbol=symbol,
                    interval=interval,
                    timestamp=bar.timestamp,
                    open=bar.open,
                    high=bar.high,
                    low=bar.low,
                    close=bar.close,
                    volume=bar.volume,
                )
                .on_conflict_do_nothing(
                    constraint="uq_stock_data_cache"
                )
            )
            await session.execute(stmt)
        await session.commit()
