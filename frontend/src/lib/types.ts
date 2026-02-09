export interface StrategyInfo {
  name: string;
  display_name: string;
  description: string;
  category: string;
}

export interface StrategyParam {
  name: string;
  label: string;
  type: string; // "int" | "float" | "select"
  default: number | string;
  min?: number;
  max?: number;
  options?: string[];
}

export interface EquityCurvePoint {
  timestamp: string;
  equity: number;
  price?: number;
}

export interface Trade {
  timestamp: string;
  symbol: string;
  side: string;
  quantity: number;
  price: number;
  fee: number;
  pnl: number | null;
}

export interface BacktestMetrics {
  total_pnl: number;
  return_pct: number;
  sharpe_ratio: number;
  max_drawdown_pct: number;
  win_rate: number;
  profit_factor: number;
  total_trades: number;
  avg_trade_duration_days: number;
}

export interface BacktestResult {
  id: string;
  metrics: BacktestMetrics;
  equity_curve: EquityCurvePoint[];
  trades: Trade[];
  indicator_data: Record<string, unknown>;
  duration_ms: number;
}

export interface Portfolio {
  positions: {
    symbol: string;
    quantity: number;
    avg_price: number;
    unrealized_pnl: number;
  }[];
}
