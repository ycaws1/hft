'use client';

import { Card, CardContent } from '@/components/ui/card';
import type { BacktestMetrics } from '@/lib/types';

interface BacktestResultsProps {
  metrics: BacktestMetrics;
  durationMs: number;
  live?: boolean;
}

export default function BacktestResults({ metrics, durationMs, live }: BacktestResultsProps) {
  const cards = [
    { label: 'Total P&L', value: `$${metrics.total_pnl.toLocaleString()}`, color: metrics.total_pnl >= 0 ? 'text-green-500' : 'text-red-500' },
    { label: 'Return', value: `${metrics.return_pct.toFixed(2)}%`, color: metrics.return_pct >= 0 ? 'text-green-500' : 'text-red-500' },
    { label: 'Sharpe Ratio', value: metrics.sharpe_ratio.toFixed(2), color: '' },
    { label: 'Max Drawdown', value: `${metrics.max_drawdown_pct.toFixed(2)}%`, color: 'text-red-500' },
    { label: 'Win Rate', value: `${metrics.win_rate.toFixed(1)}%`, color: '' },
    { label: 'Profit Factor', value: metrics.profit_factor.toFixed(2), color: '' },
    { label: 'Total Trades', value: String(metrics.total_trades), color: '' },
    ...(live ? [] : [{ label: 'Duration', value: `${(durationMs / 1000).toFixed(1)}s`, color: '' }]),
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {cards.map((c) => (
        <Card key={c.label}>
          <CardContent className="py-3 px-4">
            <p className="text-xs text-muted-foreground">{c.label}</p>
            <p className={`text-lg font-bold ${c.color}`}>{c.value}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
