import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import selectinload

from app.data.registry import registry
from app.db.session import get_db
from app.models.db_models import SimulationSession, SimulationTrade
from app.models.domain import SimulationRequest
from app.simulation.manager import simulation_manager
from app.strategies.registry import strategy_registry

router = APIRouter(prefix="/api", tags=["simulation"])


@router.post("/simulation")
async def create_simulation(
    request: SimulationRequest, db: AsyncSession = Depends(get_db)
):
    strategy = strategy_registry.get(request.strategy_name)
    provider = registry.get()
    sim_id = await simulation_manager.create_simulation(
        request, strategy, provider, db
    )
    return {"simulation_id": sim_id, "status": "running"}


@router.get("/simulation/{simulation_id}")
async def get_simulation(simulation_id: str):
    state = simulation_manager.get_simulation(simulation_id)
    if not state:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return state


@router.post("/simulation/{simulation_id}/stop")
async def stop_simulation(
    simulation_id: str, db: AsyncSession = Depends(get_db)
):
    try:
        state = await simulation_manager.stop_simulation(simulation_id, db)
        return state
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/simulations/{simulation_id}")
async def get_simulation_detail(
    simulation_id: str, db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(SimulationSession)
        .where(SimulationSession.id == uuid.UUID(simulation_id))
        .options(selectinload(SimulationSession.trades))
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Simulation not found")

    trades = sorted(session.trades, key=lambda t: t.timestamp)
    return {
        "id": str(session.id),
        "strategy_name": session.strategy_name,
        "params": session.params,
        "symbols": session.symbols,
        "mode": session.mode,
        "interval": session.interval,
        "speed": float(session.speed),
        "initial_cash": float(session.initial_cash),
        "trading_fee_pct": float(session.trading_fee_pct),
        "status": session.status,
        "started_at": session.started_at.isoformat() if session.started_at else None,
        "stopped_at": session.stopped_at.isoformat() if session.stopped_at else None,
        "final_metrics": session.final_metrics,
        "error_message": session.error_message,
        "trades": [
            {
                "timestamp": t.timestamp.isoformat(),
                "symbol": t.symbol,
                "side": t.side,
                "quantity": float(t.quantity),
                "price": float(t.price),
                "fee": float(t.fee),
                "pnl": float(t.pnl) if t.pnl is not None else None,
            }
            for t in trades
        ],
    }


@router.delete("/simulations/{simulation_id}")
async def delete_simulation(
    simulation_id: str, db: AsyncSession = Depends(get_db)
):
    stmt = select(SimulationSession).where(
        SimulationSession.id == uuid.UUID(simulation_id)
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Simulation not found")
    await db.delete(session)
    await db.commit()
    return {"status": "deleted"}


@router.get("/simulations")
async def list_simulations(
    limit: int = 20, offset: int = 0, db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(SimulationSession)
        .order_by(SimulationSession.started_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    sessions = result.scalars().all()
    return [
        {
            "id": str(s.id),
            "strategy_name": s.strategy_name,
            "symbols": s.symbols,
            "mode": s.mode,
            "speed": float(s.speed),
            "status": s.status,
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "stopped_at": s.stopped_at.isoformat() if s.stopped_at else None,
            "final_metrics": s.final_metrics,
        }
        for s in sessions
    ]
