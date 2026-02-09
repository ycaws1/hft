import asyncio
from datetime import datetime
from enum import Enum

from app.data.provider import DataProvider
from app.models.domain import SimulationMode


class SimulationClock:
    def __init__(self, mode: SimulationMode, speed: float = 1.0):
        self.mode = mode
        self.speed = speed
        self._paused = False
        self._stopped = False

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    def stop(self):
        self._stopped = True

    def set_speed(self, speed: float):
        self.speed = max(0.1, min(speed, 100.0))

    async def ticks(self, provider: DataProvider, symbols: list[str], start=None, end=None, interval="1d"):
        if self.mode == SimulationMode.REPLAY:
            # Fetch all historical data upfront, then yield one bar at a time
            from datetime import datetime as dt
            s = start or dt(2024, 1, 1)
            e = end or dt.now()
            bars = await provider.get_historical(symbols[0], s, e, interval)
            for bar in bars:
                if self._stopped:
                    return
                while self._paused:
                    if self._stopped:
                        return
                    await asyncio.sleep(0.1)
                prices = {symbols[0]: bar.close}
                yield bar.timestamp, prices
                await asyncio.sleep(1.0 / self.speed)
        else:
            # REALTIME mode - poll every second
            while not self._stopped:
                while self._paused:
                    if self._stopped:
                        return
                    await asyncio.sleep(0.1)
                prices = {}
                for s in symbols:
                    try:
                        prices[s] = await provider.get_latest_price(s)
                    except Exception:
                        pass
                if prices:
                    yield datetime.now(), prices
                await asyncio.sleep(1)
