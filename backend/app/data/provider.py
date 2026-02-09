import asyncio
from abc import ABC, abstractmethod
from datetime import datetime

from app.models.domain import OHLCV, StockSearchResult


class DataProvider(ABC):
    """Abstract interface for market data providers.

    To add a new provider, subclass this and implement all abstract methods,
    then register it with the DataProviderRegistry.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique provider identifier, e.g. 'yahoo', 'alpaca'."""

    @abstractmethod
    async def get_historical(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        interval: str = "1d",
    ) -> list[OHLCV]:
        """Fetch historical OHLCV bars."""

    @abstractmethod
    async def get_latest_price(self, symbol: str) -> float:
        """Get the most recent price for a symbol."""

    @abstractmethod
    async def search_symbols(self, query: str) -> list[StockSearchResult]:
        """Search for stock symbols matching a query string."""

    async def stream_prices(self, symbol: str):
        """Yield real-time price ticks. Default implementation polls get_latest_price."""
        while True:
            price = await self.get_latest_price(symbol)
            yield price
            await asyncio.sleep(1)
