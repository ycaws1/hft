'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import dynamic from 'next/dynamic';
import BacktestResults from '@/components/BacktestResults';
const BacktestChart = dynamic(() => import('@/components/BacktestChart'), { ssr: false });
import TradeLog from '@/components/TradeLog';
import { apiFetch } from '@/lib/api';
import type { BacktestMetrics, EquityCurvePoint, Trade } from '@/lib/types';

interface BacktestDetail {
  id: string;
  symbols: string[];
  strategy_name: string;
  params: Record<string, number | string>;
  start_date: string;
  end_date: string;
  interval: string;
  initial_cash: number;
  metrics: BacktestMetrics;
  equity_curve: EquityCurvePoint[];
  trades: Trade[];
  indicator_data: Record<string, unknown>;
  created_at: string | null;
  duration_ms: number;
}

export default function BacktestDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const [detail, setDetail] = useState<BacktestDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    apiFetch<BacktestDetail>(`/api/backtests/${id}`)
      .then(setDetail)
      .catch((e) => setError(e.message));
  }, [id]);

  const handleDelete = async () => {
    try {
      await apiFetch(`/api/backtests/${id}`, { method: 'DELETE' });
      router.push('/');
    } catch { /* ignore */ }
  };

  if (error) {
    return (
      <div className="space-y-4">
        <Button variant="outline" onClick={() => router.back()}>Back</Button>
        <p className="text-red-500">{error}</p>
      </div>
    );
  }

  if (!detail) {
    return <p className="text-muted-foreground">Loading...</p>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="sm" onClick={() => router.back()}>
          Back
        </Button>
        <h1 className="text-3xl font-bold">Backtest Detail</h1>
        <Button variant="destructive" size="sm" className="ml-auto" onClick={handleDelete}>
          Delete
        </Button>
      </div>

      <div className="flex flex-wrap gap-x-6 gap-y-1 text-sm text-muted-foreground">
        <span>Strategy: <span className="text-foreground font-medium">{detail.strategy_name}</span></span>
        <span>Symbols: <span className="text-foreground font-medium">{detail.symbols.join(', ')}</span></span>
        <span>Period: <span className="text-foreground font-medium">{detail.start_date} to {detail.end_date}</span></span>
        <span>Interval: <span className="text-foreground font-medium">{detail.interval}</span></span>
        <span>Cash: <span className="text-foreground font-medium">${detail.initial_cash.toLocaleString()}</span></span>
        {detail.created_at && (
          <span>Run at: <span className="text-foreground font-medium">{new Date(detail.created_at).toLocaleString()}</span></span>
        )}
      </div>

      <BacktestResults metrics={detail.metrics} durationMs={detail.duration_ms} />
      <BacktestChart equityCurve={detail.equity_curve} trades={detail.trades} />
      <TradeLog trades={detail.trades} />
    </div>
  );
}
