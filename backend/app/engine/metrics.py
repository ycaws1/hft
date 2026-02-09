import math

from app.models.domain import BacktestMetrics, Fill


def compute_metrics(
    equity_curve: list[dict],
    fills: list[Fill],
    initial_cash: float,
) -> BacktestMetrics:
    equities = [pt["equity"] for pt in equity_curve]
    final_equity = equities[-1] if equities else initial_cash

    total_pnl = final_equity - initial_cash
    return_pct = (final_equity / initial_cash - 1) * 100 if initial_cash > 0 else 0

    # Daily returns
    daily_returns = []
    for i in range(1, len(equities)):
        if equities[i - 1] > 0:
            daily_returns.append(equities[i] / equities[i - 1] - 1)

    # Sharpe Ratio (annualized, assuming 252 trading days)
    if daily_returns and len(daily_returns) > 1:
        mean_ret = sum(daily_returns) / len(daily_returns)
        std_ret = (sum((r - mean_ret) ** 2 for r in daily_returns) / (len(daily_returns) - 1)) ** 0.5
        sharpe_ratio = (mean_ret / std_ret * math.sqrt(252)) if std_ret > 0 else 0.0
    else:
        sharpe_ratio = 0.0

    # Max Drawdown
    max_drawdown_pct = 0.0
    peak = equities[0] if equities else initial_cash
    for eq in equities:
        if eq > peak:
            peak = eq
        drawdown = (peak - eq) / peak * 100 if peak > 0 else 0
        if drawdown > max_drawdown_pct:
            max_drawdown_pct = drawdown

    # Win rate & profit factor
    sell_fills = [f for f in fills if f.side.value == "SELL" and f.pnl is not None]
    total_trades = len(sell_fills)
    winning = [f for f in sell_fills if f.pnl > 0]
    win_rate = len(winning) / total_trades if total_trades > 0 else 0.0

    gross_profit = sum(f.pnl for f in sell_fills if f.pnl > 0)
    gross_loss = abs(sum(f.pnl for f in sell_fills if f.pnl < 0))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf") if gross_profit > 0 else 0.0

    # Avg trade duration (simple: spread fills evenly over the period)
    if total_trades > 0 and len(equity_curve) > 1:
        total_days = (len(equity_curve) - 1)
        avg_trade_duration_days = total_days / total_trades
    else:
        avg_trade_duration_days = 0.0

    return BacktestMetrics(
        total_pnl=round(total_pnl, 2),
        return_pct=round(return_pct, 2),
        sharpe_ratio=round(sharpe_ratio, 4),
        max_drawdown_pct=round(-max_drawdown_pct, 2),
        win_rate=round(win_rate, 4),
        profit_factor=round(min(profit_factor, 999.99), 2),
        total_trades=total_trades,
        avg_trade_duration_days=round(avg_trade_duration_days, 1),
    )
