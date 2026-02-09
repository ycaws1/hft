import asyncio
from datetime import datetime
from functools import partial

import yfinance as yf

from app.data.provider import DataProvider
from app.models.domain import OHLCV, StockSearchResult


class YahooFinanceProvider(DataProvider):
    @property
    def name(self) -> str:
        return "yahoo"

    async def get_historical(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        interval: str = "1d",
    ) -> list[OHLCV]:
        loop = asyncio.get_event_loop()
        df = await loop.run_in_executor(
            None,
            partial(
                self._fetch_history,
                symbol=symbol,
                start=start.strftime("%Y-%m-%d"),
                end=end.strftime("%Y-%m-%d"),
                interval=interval,
            ),
        )
        if df is None or df.empty:
            return []

        bars = []
        for idx, row in df.iterrows():
            bars.append(
                OHLCV(
                    timestamp=idx.to_pydatetime(),
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=int(row["Volume"]),
                )
            )
        return bars

    async def get_latest_price(self, symbol: str) -> float:
        loop = asyncio.get_event_loop()
        ticker = await loop.run_in_executor(None, partial(yf.Ticker, symbol))
        info = await loop.run_in_executor(None, lambda: ticker.fast_info)
        return float(info["lastPrice"])

    async def search_symbols(self, query: str) -> list[StockSearchResult]:
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, partial(self._search, query))
        return results

    @staticmethod
    def _fetch_history(symbol: str, start: str, end: str, interval: str):
        ticker = yf.Ticker(symbol)
        return ticker.history(start=start, end=end, interval=interval)

    @staticmethod
    def _search(query: str) -> list[StockSearchResult]:
        # Try yf.Search first
        try:
            results = yf.Search(query)
            if results.quotes:
                out = []
                for q in results.quotes[:10]:
                    out.append(
                        StockSearchResult(
                            symbol=q.get("symbol", ""),
                            name=q.get("shortname", q.get("longname", "")),
                            exchange=q.get("exchange", ""),
                        )
                    )
                if out:
                    return out
        except Exception:
            pass

        # Fallback: treat query as a ticker symbol and validate via yf.Ticker
        try:
            ticker = yf.Ticker(query.upper())
            info = ticker.info
            if info and info.get("quoteType"):
                return [
                    StockSearchResult(
                        symbol=query.upper(),
                        name=info.get("shortName", info.get("longName", query.upper())),
                        exchange=info.get("exchange", ""),
                    )
                ]
        except Exception:
            pass

        return []
