import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.registry import registry
from app.db.session import get_db
from app.engine.backtester import BacktestEngine
from app.models.db_models import BacktestRun
from app.models.domain import BacktestRequest, BacktestResult
from app.strategies.registry import strategy_registry

router = APIRouter(prefix="/api", tags=["backtest"])


@router.post("/backtest", response_model=BacktestResult)
async def run_backtest(request: BacktestRequest, db: AsyncSession = Depends(get_db)):
    strategy = strategy_registry.get(request.strategy_name)
    provider = registry.get()
    engine = BacktestEngine(provider)
    result = await engine.run(request, strategy)

    # Persist to DB
    db_run = BacktestRun(
        id=uuid.UUID(result.id),
        symbols=request.symbols,
        strategy_name=request.strategy_name,
        params=request.params,
        start_date=request.start_date,
        end_date=request.end_date,
        interval=request.interval,
        initial_cash=request.initial_cash,
        metrics=result.metrics.model_dump(),
        equity_curve=result.equity_curve,
        trades=result.trades,
        indicator_data=result.indicator_data,
        duration_ms=result.duration_ms,
    )
    db.add(db_run)
    await db.commit()

    return result


@router.get("/backtests")
async def list_backtests(
    limit: int = 20, offset: int = 0, db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(BacktestRun)
        .order_by(BacktestRun.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    runs = result.scalars().all()
    return [
        {
            "id": str(run.id),
            "symbols": run.symbols,
            "strategy_name": run.strategy_name,
            "params": run.params,
            "start_date": str(run.start_date),
            "end_date": str(run.end_date),
            "metrics": run.metrics,
            "created_at": run.created_at.isoformat() if run.created_at else None,
            "duration_ms": run.duration_ms,
        }
        for run in runs
    ]


@router.delete("/backtests/{backtest_id}")
async def delete_backtest(backtest_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(BacktestRun).where(BacktestRun.id == uuid.UUID(backtest_id))
    result = await db.execute(stmt)
    run = result.scalar_one_or_none()
    if not run:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Backtest not found")
    await db.delete(run)
    await db.commit()
    return {"status": "deleted"}


@router.get("/backtests/{backtest_id}")
async def get_backtest(backtest_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(BacktestRun).where(BacktestRun.id == uuid.UUID(backtest_id))
    result = await db.execute(stmt)
    run = result.scalar_one_or_none()
    if not run:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Backtest not found")
    return {
        "id": str(run.id),
        "symbols": run.symbols,
        "strategy_name": run.strategy_name,
        "params": run.params,
        "start_date": str(run.start_date),
        "end_date": str(run.end_date),
        "interval": run.interval,
        "initial_cash": float(run.initial_cash),
        "metrics": run.metrics,
        "equity_curve": run.equity_curve,
        "trades": run.trades,
        "indicator_data": run.indicator_data,
        "created_at": run.created_at.isoformat() if run.created_at else None,
        "duration_ms": run.duration_ms,
    }
