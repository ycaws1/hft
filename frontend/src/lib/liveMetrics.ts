import type { BacktestMetrics, EquityCurvePoint, Trade } from '@/lib/types';

export function computeLiveMetrics(
  equityCurve: EquityCurvePoint[],
  trades: Trade[],
  initialCash: number
): BacktestMetrics {
  const lastEquity =
    equityCurve.length > 0 ? equityCurve[equityCurve.length - 1].equity : initialCash;
  const totalPnl = lastEquity - initialCash;
  const returnPct = initialCash > 0 ? (totalPnl / initialCash) * 100 : 0;

  // Max drawdown
  let peak = initialCash;
  let maxDd = 0;
  for (const pt of equityCurve) {
    if (pt.equity > peak) peak = pt.equity;
    const dd = ((peak - pt.equity) / peak) * 100;
    if (dd > maxDd) maxDd = dd;
  }

  // Win rate & profit factor
  const closedTrades = trades.filter((t) => t.pnl != null);
  const wins = closedTrades.filter((t) => (t.pnl ?? 0) > 0);
  const losses = closedTrades.filter((t) => (t.pnl ?? 0) < 0);
  const winRate =
    closedTrades.length > 0 ? (wins.length / closedTrades.length) * 100 : 0;
  const grossProfit = wins.reduce((s, t) => s + (t.pnl ?? 0), 0);
  const grossLoss = Math.abs(losses.reduce((s, t) => s + (t.pnl ?? 0), 0));
  const profitFactor = grossLoss > 0 ? grossProfit / grossLoss : grossProfit > 0 ? Infinity : 0;

  // Simple Sharpe (daily returns)
  let sharpe = 0;
  if (equityCurve.length > 1) {
    const returns: number[] = [];
    for (let i = 1; i < equityCurve.length; i++) {
      const prev = equityCurve[i - 1].equity;
      if (prev > 0) returns.push((equityCurve[i].equity - prev) / prev);
    }
    if (returns.length > 0) {
      const mean = returns.reduce((a, b) => a + b, 0) / returns.length;
      const variance =
        returns.reduce((a, r) => a + (r - mean) ** 2, 0) / returns.length;
      const std = Math.sqrt(variance);
      sharpe = std > 0 ? (mean / std) * Math.sqrt(252) : 0;
    }
  }

  return {
    total_pnl: Math.round(totalPnl * 100) / 100,
    return_pct: Math.round(returnPct * 100) / 100,
    sharpe_ratio: Math.round(sharpe * 100) / 100,
    max_drawdown_pct: Math.round(maxDd * 100) / 100,
    win_rate: Math.round(winRate * 100) / 100,
    profit_factor: profitFactor === Infinity ? 999 : Math.round(profitFactor * 100) / 100,
    total_trades: trades.length,
    avg_trade_duration_days: 0,
  };
}
