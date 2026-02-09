from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel


class OHLCV(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class StockSearchResult(BaseModel):
    symbol: str
    name: str
    exchange: str


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class Order(BaseModel):
    symbol: str
    side: OrderSide
    quantity: float
    order_type: str = "MARKET"


class Fill(BaseModel):
    timestamp: datetime
    symbol: str
    side: OrderSide
    quantity: float
    price: float
    fee: float = 0.0
    pnl: float | None = None
    order_id: str | None = None


class Position(BaseModel):
    symbol: str
    quantity: float
    avg_price: float
    unrealized_pnl: float = 0.0


class PortfolioSnapshot(BaseModel):
    timestamp: datetime
    cash: float
    total_equity: float
    positions: list[Position]


class StrategyParamDef(BaseModel):
    name: str
    label: str
    type: str  # "int", "float", "select"
    default: float | str
    min: float | None = None
    max: float | None = None
    options: list[str] | None = None


class StrategyInfo(BaseModel):
    name: str
    display_name: str
    description: str
    category: str


class BacktestRequest(BaseModel):
    symbols: list[str]
    strategy_name: str
    params: dict
    start_date: date
    end_date: date
    interval: str = "1d"
    initial_cash: float = 100000.0
    trading_fee_pct: float = 1.0  # percentage per trade, default 1%


class BacktestMetrics(BaseModel):
    total_pnl: float
    return_pct: float
    sharpe_ratio: float
    max_drawdown_pct: float
    win_rate: float
    profit_factor: float
    total_trades: int
    avg_trade_duration_days: float


class BacktestResult(BaseModel):
    id: str
    metrics: BacktestMetrics
    equity_curve: list[dict]
    trades: list[dict]
    indicator_data: dict
    duration_ms: int


class SimulationMode(str, Enum):
    REALTIME = "realtime"
    REPLAY = "replay"


class SimulationRequest(BaseModel):
    strategy_name: str
    params: dict
    symbols: list[str]
    mode: SimulationMode = SimulationMode.REPLAY
    speed: float = 1.0
    interval: str = "1d"
    start_date: date | None = None
    end_date: date | None = None
    initial_cash: float = 100000.0
    trading_fee_pct: float = 1.0  # percentage per trade, default 1%
