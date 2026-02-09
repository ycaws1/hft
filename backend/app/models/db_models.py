import uuid
from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class StockDataCache(Base):
    __tablename__ = "stock_data_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    interval: Mapped[str] = mapped_column(String(10), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    open: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    high: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    low: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    close: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("symbol", "interval", "timestamp", name="uq_stock_data_cache"),
    )


class BacktestRun(Base):
    __tablename__ = "backtest_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    symbols: Mapped[dict] = mapped_column(JSONB, nullable=False)
    strategy_name: Mapped[str] = mapped_column(String(50), nullable=False)
    params: Mapped[dict] = mapped_column(JSONB, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    interval: Mapped[str] = mapped_column(String(10), nullable=False)
    initial_cash: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    metrics: Mapped[dict] = mapped_column(JSONB, nullable=True)
    equity_curve: Mapped[dict] = mapped_column(JSONB, nullable=True)
    trades: Mapped[dict] = mapped_column(JSONB, nullable=True)
    indicator_data: Mapped[dict] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=True)


class SimulationSession(Base):
    __tablename__ = "simulation_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    strategy_name: Mapped[str] = mapped_column(String(50), nullable=False)
    params: Mapped[dict] = mapped_column(JSONB, nullable=False)
    symbols: Mapped[dict] = mapped_column(JSONB, nullable=False)
    mode: Mapped[str] = mapped_column(String(20), nullable=False)
    speed: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False, default=1.0)
    interval: Mapped[str] = mapped_column(String(10), nullable=False, default="1d")
    initial_cash: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    trading_fee_pct: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False, default=1.0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="running")
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    stopped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    final_metrics: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    trades: Mapped[list["SimulationTrade"]] = relationship(
        back_populates="simulation", cascade="all, delete-orphan"
    )


class SimulationTrade(Base):
    __tablename__ = "simulation_trades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    simulation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("simulation_sessions.id", ondelete="CASCADE"), nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    side: Mapped[str] = mapped_column(String(4), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    fee: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    pnl: Mapped[float | None] = mapped_column(Numeric(14, 4), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    simulation: Mapped["SimulationSession"] = relationship(back_populates="trades")

    __table_args__ = (
        Index("ix_simulation_trades_sim_id", "simulation_id"),
    )
