import logging
import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.provider import DataProvider
from app.models.db_models import SimulationSession, SimulationTrade
from app.models.domain import SimulationMode, SimulationRequest
from app.simulation.broker import SimulatedBroker
from app.simulation.clock import SimulationClock
from app.simulation.runner import SimulationRunner
from app.strategies.base import Strategy

logger = logging.getLogger(__name__)


class SimulationManager:
    """Manages the lifecycle of live simulation runners."""

    def __init__(self):
        self._runners: dict[str, SimulationRunner] = {}
        self._ws_subscribers: dict[str, list] = {}  # simulation_id -> [websocket, ...]

    async def create_simulation(
        self,
        request: SimulationRequest,
        strategy: Strategy,
        provider: DataProvider,
        db: AsyncSession,
    ) -> str:
        """Create and start a new simulation. Returns simulation_id."""
        sim_id = str(uuid.uuid4())
        params = strategy.validate_params(request.params)

        # Persist session to DB
        db_session = SimulationSession(
            id=uuid.UUID(sim_id),
            strategy_name=request.strategy_name,
            params=params,
            symbols=request.symbols,
            mode=request.mode.value,
            speed=request.speed,
            interval=request.interval,
            initial_cash=request.initial_cash,
            trading_fee_pct=request.trading_fee_pct,
            status="running",
        )
        db.add(db_session)
        await db.commit()

        # Create simulation components
        broker = SimulatedBroker(
            initial_cash=request.initial_cash,
            fee_pct=request.trading_fee_pct,
        )
        clock = SimulationClock(mode=request.mode, speed=request.speed)

        # Build the on_update callback that broadcasts to WebSocket subscribers
        # and writes trades to DB
        async def on_update(update: dict):
            # Write trade to DB if present
            if "trade" in update:
                trade_data = update["trade"]
                try:
                    from app.db.engine import async_session as session_factory
                    async with session_factory() as trade_db:
                        db_trade = SimulationTrade(
                            simulation_id=uuid.UUID(sim_id),
                            timestamp=datetime.fromisoformat(update["timestamp"]),
                            symbol=trade_data["symbol"],
                            side=trade_data["side"],
                            quantity=trade_data["quantity"],
                            price=trade_data["price"],
                            fee=trade_data.get("fee", 0),
                            pnl=trade_data.get("pnl"),
                        )
                        trade_db.add(db_trade)
                        await trade_db.commit()
                except Exception as e:
                    logger.error("Failed to persist trade: %s", e)

            # Broadcast to WebSocket subscribers
            subscribers = self._ws_subscribers.get(sim_id, [])
            disconnected = []
            for ws in subscribers:
                try:
                    await ws.send_json(update)
                except Exception:
                    disconnected.append(ws)
            for ws in disconnected:
                subscribers.remove(ws)

        # Convert date to datetime for clock
        from datetime import datetime as dt
        start_dt = dt.combine(request.start_date, dt.min.time()) if request.start_date else None
        end_dt = dt.combine(request.end_date, dt.min.time()) if request.end_date else None

        # on_complete callback: finalize when replay finishes naturally
        async def on_complete(r: SimulationRunner):
            await self._finalize_simulation(r)

        runner = SimulationRunner(
            simulation_id=sim_id,
            strategy=strategy,
            params=params,
            symbols=request.symbols,
            provider=provider,
            broker=broker,
            clock=clock,
            on_update=on_update,
            on_complete=on_complete,
            interval=request.interval,
            start_date=start_dt,
            end_date=end_dt,
        )

        self._runners[sim_id] = runner
        self._ws_subscribers[sim_id] = []
        runner.start()

        logger.info(
            "Simulation %s started: strategy=%s symbols=%s mode=%s",
            sim_id,
            request.strategy_name,
            request.symbols,
            request.mode.value,
        )
        return sim_id

    async def _finalize_simulation(self, runner: SimulationRunner):
        """Persist final state to DB and notify WS subscribers. Used by both manual stop and auto-complete."""
        simulation_id = runner.simulation_id
        state = runner.get_state()

        # Build final_metrics including equity curve for later viewing
        final_metrics = {
            "equity": state["equity"],
            "cash": state["cash"],
            "total_trades": state["total_trades"],
            "total_fees": round(runner.broker.total_fees, 2),
            "return_pct": round(
                (state["equity"] / runner.broker.portfolio.initial_cash - 1) * 100, 2
            ),
            "equity_curve": runner._equity_curve,
        }

        # Update DB record
        try:
            from app.db.engine import async_session as session_factory
            async with session_factory() as db:
                stmt = (
                    update(SimulationSession)
                    .where(SimulationSession.id == uuid.UUID(simulation_id))
                    .values(
                        status=runner.status,
                        stopped_at=datetime.now(),
                        final_metrics=final_metrics,
                        error_message=runner.error,
                    )
                )
                await db.execute(stmt)
                await db.commit()
        except Exception as e:
            logger.error("Failed to finalize simulation %s: %s", simulation_id, e)

        # Notify WebSocket subscribers
        subscribers = self._ws_subscribers.get(simulation_id, [])
        for ws in subscribers:
            try:
                await ws.send_json({"type": "stopped", "status": runner.status, "simulation_id": simulation_id, **state})
            except Exception:
                pass

        logger.info("Simulation %s finalized (status=%s)", simulation_id, runner.status)

    async def stop_simulation(self, simulation_id: str, db: AsyncSession) -> dict:
        """Stop a running simulation and persist final state."""
        runner = self._runners.get(simulation_id)
        if not runner:
            raise ValueError(f"Simulation {simulation_id} not found")

        await runner.stop()
        await self._finalize_simulation(runner)
        return runner.get_state()

    def get_simulation(self, simulation_id: str) -> dict | None:
        """Get the current state of a simulation."""
        runner = self._runners.get(simulation_id)
        if not runner:
            return None
        return runner.get_state()

    def get_runner(self, simulation_id: str) -> SimulationRunner | None:
        """Get the runner instance for clock control."""
        return self._runners.get(simulation_id)

    def subscribe_ws(self, simulation_id: str, websocket):
        """Register a WebSocket to receive live updates."""
        if simulation_id not in self._ws_subscribers:
            self._ws_subscribers[simulation_id] = []
        self._ws_subscribers[simulation_id].append(websocket)

    def unsubscribe_ws(self, simulation_id: str, websocket):
        """Remove a WebSocket subscriber."""
        subs = self._ws_subscribers.get(simulation_id, [])
        if websocket in subs:
            subs.remove(websocket)


# Singleton instance shared across the application
simulation_manager = SimulationManager()
