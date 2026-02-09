'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { apiFetch } from '@/lib/api';

interface BacktestSummary {
  id: string;
  symbols: string[];
  strategy_name: string;
  metrics: { return_pct: number; sharpe_ratio: number; total_trades: number };
  created_at: string | null;
}

interface SimulationSummary {
  id: string;
  strategy_name: string;
  symbols: string[];
  mode: string;
  status: string;
  started_at: string | null;
  final_metrics: { return_pct?: number } | null;
}

export default function DashboardPage() {
  const [backtests, setBacktests] = useState<BacktestSummary[]>([]);
  const [simulations, setSimulations] = useState<SimulationSummary[]>([]);

  useEffect(() => {
    apiFetch<BacktestSummary[]>('/api/backtests?limit=10').then(setBacktests).catch(() => {});
    apiFetch<SimulationSummary[]>('/api/simulations?limit=10').then(setSimulations).catch(() => {});
  }, []);

  const deleteBacktest = async (e: React.MouseEvent, id: string) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      await apiFetch(`/api/backtests/${id}`, { method: 'DELETE' });
      setBacktests((prev) => prev.filter((bt) => bt.id !== id));
    } catch { /* ignore */ }
  };

  const deleteSimulation = async (e: React.MouseEvent, id: string) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      await apiFetch(`/api/simulations/${id}`, { method: 'DELETE' });
      setSimulations((prev) => prev.filter((s) => s.id !== id));
    } catch { /* ignore */ }
  };

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Dashboard</h1>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Recent Backtests */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Recent Backtests</CardTitle>
            <Link href="/backtest">
              <Button size="sm" variant="outline">New Backtest</Button>
            </Link>
          </CardHeader>
          <CardContent>
            {backtests.length === 0 ? (
              <p className="text-sm text-muted-foreground">No backtests yet</p>
            ) : (
              <div className="space-y-2">
                {backtests.map((bt) => (
                  <Link
                    key={bt.id}
                    href={`/backtest/${bt.id}`}
                    className="block rounded-md border p-3 hover:bg-accent transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="font-medium text-sm">{bt.strategy_name}</span>
                        <span className="text-xs text-muted-foreground ml-2">
                          {bt.symbols.join(', ')}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`text-sm font-medium ${bt.metrics.return_pct >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                          {bt.metrics.return_pct.toFixed(2)}%
                        </span>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-6 w-6 p-0 text-muted-foreground hover:text-red-500"
                          onClick={(e) => deleteBacktest(e, bt.id)}
                        >
                          &times;
                        </Button>
                      </div>
                    </div>
                    {bt.created_at && (
                      <p className="text-xs text-muted-foreground mt-1">
                        {new Date(bt.created_at).toLocaleString()}
                      </p>
                    )}
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Simulations */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Recent Simulations</CardTitle>
            <Link href="/simulation">
              <Button size="sm" variant="outline">New Simulation</Button>
            </Link>
          </CardHeader>
          <CardContent>
            {simulations.length === 0 ? (
              <p className="text-sm text-muted-foreground">No simulations yet</p>
            ) : (
              <div className="space-y-2">
                {simulations.map((sim) => (
                  <Link
                    key={sim.id}
                    href={`/simulation/${sim.id}`}
                    className="block rounded-md border p-3 hover:bg-accent transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="font-medium text-sm">{sim.strategy_name}</span>
                        <span className="text-xs text-muted-foreground ml-2">
                          {sim.symbols.join(', ')}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={sim.status === 'running' ? 'default' : 'secondary'} className="text-xs">
                          {sim.status}
                        </Badge>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-6 w-6 p-0 text-muted-foreground hover:text-red-500"
                          onClick={(e) => deleteSimulation(e, sim.id)}
                        >
                          &times;
                        </Button>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-muted-foreground">{sim.mode}</span>
                      {sim.final_metrics?.return_pct !== undefined && (
                        <span className={`text-xs font-medium ${sim.final_metrics.return_pct >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                          {sim.final_metrics.return_pct.toFixed(2)}%
                        </span>
                      )}
                      {sim.started_at && (
                        <span className="text-xs text-muted-foreground">
                          {new Date(sim.started_at).toLocaleString()}
                        </span>
                      )}
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
