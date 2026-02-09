import asyncio
import logging
from datetime import datetime
from typing import Callable, Awaitable

import pandas as pd

from app.data.provider import DataProvider
from app.models.domain import Order, OrderSide, SimulationMode
from app.simulation.broker import SimulatedBroker
from app.simulation.clock import SimulationClock
from app.strategies.base import Strategy

logger = logging.getLogger(__name__)


class SimulationRunner:
    """Runs a strategy in an async loop driven by SimulationClock ticks."""

    def __init__(
        self,
        simulation_id: str,
        strategy: Strategy,
        params: dict,
        symbols: list[str],
        provider: DataProvider,
        broker: SimulatedBroker,
        clock: SimulationClock,
        on_update: Callable[[dict], Awaitable[None]] | None = None,
        on_complete: Callable[["SimulationRunner"], Awaitable[None]] | None = None,
        interval: str = "1d",
        start_date=None,
        end_date=None,
    ):
        self.simulation_id = simulation_id
        self.strategy = strategy
        self.params = params
        self.symbols = symbols
        self.provider = provider
        self.broker = broker
        self.clock = clock
        self.on_update = on_update
        self.on_complete = on_complete
        self.interval = interval
        self.start_date = start_date
        self.end_date = end_date

        self._task: asyncio.Task | None = None
        self._price_history: list[dict] = []
        self._equity_curve: list[dict] = []
        self._tick_count = 0
        self.status = "pending"
        self.error: str | None = None

    def start(self):
        """Launch the simulation loop as a background asyncio task."""
        self._task = asyncio.create_task(self._run())

    async def stop(self):
        """Stop the simulation gracefully."""
        self.clock.stop()
        if self._task and not self._task.done():
            try:
                await asyncio.wait_for(self._task, timeout=5.0)
            except asyncio.TimeoutError:
                self._task.cancel()
        self.status = "stopped"

    async def _run(self):
        """Main simulation loop."""
        self.status = "running"
        try:
            async for timestamp, prices in self.clock.ticks(
                self.provider, self.symbols,
                start=self.start_date, end=self.end_date,
                interval=self.interval,
            ):
                self._tick_count += 1

                # Accumulate price history for signal generation
                primary_symbol = self.symbols[0]
                price = prices.get(primary_symbol, 0.0)
                self._price_history.append(
                    {
                        "timestamp": timestamp,
                        "open": price,
                        "high": price,
                        "low": price,
                        "close": price,
                        "volume": 0,
                    }
                )

                # Need enough bars for the strategy to compute indicators
                signal = 0
                if len(self._price_history) >= 2:
                    df = pd.DataFrame(self._price_history)
                    try:
                        df = self.strategy.generate_signals(df, self.params)
                        signal = int(df["signal"].iloc[-1])
                    except Exception as e:
                        logger.warning(
                            "Signal generation error (tick %d): %s",
                            self._tick_count,
                            e,
                        )

                # Execute orders based on signal (position-aware)
                fill = None
                pos = self.broker.portfolio.positions.get(primary_symbol)
                has_position = pos and pos["quantity"] > 0

                if signal == 1 and not has_position:
                    # Buy only when not already holding
                    cash_to_use = self.broker.portfolio.cash * 0.10
                    qty = int(cash_to_use / price) if price > 0 else 0
                    if qty > 0:
                        fill = self.broker.submit_order(
                            Order(
                                symbol=primary_symbol,
                                side=OrderSide.BUY,
                                quantity=qty,
                            ),
                            price,
                            timestamp,
                        )
                elif signal == -1 and has_position:
                    # Sell only when holding a position
                    fill = self.broker.submit_order(
                        Order(
                            symbol=primary_symbol,
                            side=OrderSide.SELL,
                            quantity=pos["quantity"],
                        ),
                        price,
                        timestamp,
                    )

                # Build update payload and push to WebSocket listeners
                equity = self.broker.portfolio.get_equity(prices)
                snapshot = self.broker.portfolio.snapshot(timestamp, prices)

                ts_str = (
                    timestamp.isoformat()
                    if hasattr(timestamp, "isoformat")
                    else str(timestamp)
                )

                # Track equity curve for persistence
                self._equity_curve.append(
                    {"timestamp": ts_str, "equity": round(equity, 2), "price": round(price, 4)}
                )

                update = {
                    "type": "tick",
                    "simulation_id": self.simulation_id,
                    "tick": self._tick_count,
                    "timestamp": ts_str,
                    "prices": {k: round(v, 4) for k, v in prices.items()},
                    "signal": signal,
                    "equity": round(equity, 2),
                    "cash": round(snapshot.cash, 2),
                    "positions": [p.model_dump() for p in snapshot.positions],
                }

                if fill:
                    update["trade"] = {
                        "symbol": fill.symbol,
                        "side": fill.side.value,
                        "quantity": fill.quantity,
                        "price": round(fill.price, 4),
                        "fee": round(fill.fee, 2),
                        "pnl": round(fill.pnl, 2) if fill.pnl is not None else None,
                    }

                if self.on_update:
                    try:
                        await self.on_update(update)
                    except Exception as e:
                        logger.warning("on_update callback error: %s", e)

            # Simulation completed naturally (replay finished)
            self.status = "completed"
            if self.on_complete:
                try:
                    await self.on_complete(self)
                except Exception as e:
                    logger.error("on_complete callback error: %s", e)
        except asyncio.CancelledError:
            self.status = "stopped"
        except Exception as e:
            logger.exception("Simulation %s crashed", self.simulation_id)
            self.status = "error"
            self.error = str(e)

    def get_state(self) -> dict:
        """Return current simulation state for REST queries."""
        prices = {}
        if self._price_history:
            last = self._price_history[-1]
            prices = {self.symbols[0]: last["close"]}

        equity = self.broker.portfolio.get_equity(prices) if prices else self.broker.portfolio.cash
        snapshot = self.broker.portfolio.snapshot(datetime.now(), prices)

        return {
            "simulation_id": self.simulation_id,
            "status": self.status,
            "tick_count": self._tick_count,
            "equity": round(equity, 2),
            "cash": round(snapshot.cash, 2),
            "positions": [p.model_dump() for p in snapshot.positions],
            "total_trades": len(self.broker.fills),
            "speed": self.clock.speed,
            "paused": self.clock._paused,
            "error": self.error,
            "equity_curve": self._equity_curve,
        }
