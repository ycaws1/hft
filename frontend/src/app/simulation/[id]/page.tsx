'use client';

import { useEffect, useState, useMemo, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import BacktestResults from '@/components/BacktestResults';
import LiveChart from '@/components/LiveChart';
import PortfolioDashboard from '@/components/PortfolioDashboard';
import SimulationControls from '@/components/SimulationControls';
import TradeLog from '@/components/TradeLog';
import { useWebSocket } from '@/hooks/useWebSocket';
import { apiFetch } from '@/lib/api';
import { computeLiveMetrics } from '@/lib/liveMetrics';
import type { Trade, EquityCurvePoint, BacktestMetrics, Portfolio } from '@/lib/types';

const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

interface FinalMetrics {
  equity: number;
  cash: number;
  total_trades: number;
  total_fees: number;
  return_pct: number;
  equity_curve?: EquityCurvePoint[];
}

interface SimulationDetail {
  id: string;
  strategy_name: string;
  params: Record<string, number | string>;
  symbols: string[];
  mode: string;
  interval?: string;
  speed: number;
  initial_cash: number;
  trading_fee_pct: number;
  status: string;
  started_at: string | null;
  stopped_at: string | null;
  final_metrics: FinalMetrics | null;
  error_message: string | null;
  trades: Trade[];
}

interface RunnerState {
  simulation_id: string;
  status: string;
  tick_count: number;
  equity: number;
  cash: number;
  positions: Portfolio['positions'];
  total_trades: number;
  speed: number;
  paused: boolean;
  error: string | null;
  equity_curve: EquityCurvePoint[];
}

export default function SimulationDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const simulationId = id as string;

  // DB data for stopped/completed simulations
  const [detail, setDetail] = useState<SimulationDetail | null>(null);
  // Runner state for running simulations
  const [runnerState, setRunnerState] = useState<RunnerState | null>(null);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);

  // Whether the runner is alive in memory (not just a DB record)
  const [runnerAlive, setRunnerAlive] = useState(false);

  // Live state accumulated from WebSocket
  const [simStatus, setSimStatus] = useState<string>('loading');
  const [equity, setEquity] = useState(0);
  const [cash, setCash] = useState(0);
  const [positions, setPositions] = useState<Portfolio['positions']>([]);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [equityCurve, setEquityCurve] = useState<EquityCurvePoint[]>([]);
  const [tickCount, setTickCount] = useState(0);
  const [speed, setSpeed] = useState(1);
  const [paused, setPaused] = useState(false);
  const [initialCash, setInitialCash] = useState(100000);

  // Fetch data on mount
  useEffect(() => {
    if (!simulationId) return;

    // Try to get live runner state first
    apiFetch<RunnerState>(`/api/simulation/${simulationId}`)
      .then((state) => {
        // Runner exists — simulation is in memory (running/stopped/completed)
        setRunnerAlive(true);
        setRunnerState(state);
        setSimStatus(state.status);
        setEquity(state.equity);
        setCash(state.cash);
        setPositions(state.positions || []);
        setTickCount(state.tick_count);
        setSpeed(state.speed);
        setPaused(state.paused);
        // Restore full equity curve history from runner
        if (state.equity_curve && state.equity_curve.length > 0) {
          setEquityCurve(state.equity_curve);
        }
        setLoading(false);
      })
      .catch(() => {
        // Runner not in memory — load from DB
        apiFetch<SimulationDetail>(`/api/simulations/${simulationId}`)
          .then((data) => {
            setDetail(data);
            // If DB says "running" but runner is gone, it's stale
            setSimStatus(data.status === 'running' ? 'stopped' : data.status);
            setTrades(data.trades);
            setInitialCash(data.initial_cash);
            // Restore equity curve from final_metrics if available
            if (data.final_metrics?.equity_curve && data.final_metrics.equity_curve.length > 0) {
              setEquityCurve(data.final_metrics.equity_curve);
            }
            setLoading(false);
          })
          .catch((e) => {
            setFetchError(e.message);
            setLoading(false);
          });
      });
  }, [simulationId]);

  // Also fetch DB detail for initial_cash even when runner is alive
  useEffect(() => {
    if (!simulationId || detail) return;
    apiFetch<SimulationDetail>(`/api/simulations/${simulationId}`)
      .then((data) => {
        setDetail(data);
        setInitialCash(data.initial_cash);
        // If we already have runner trades in the WS feed, don't overwrite
        if (trades.length === 0 && data.trades.length > 0) {
          setTrades(data.trades);
        }
      })
      .catch(() => {});
  }, [simulationId]);

  // WebSocket — connect only if runner is alive and status is running
  const wsUrl = useMemo(
    () =>
      simulationId && runnerAlive && simStatus === 'running'
        ? `${WS_BASE}/ws/simulation/${simulationId}`
        : null,
    [simulationId, runnerAlive, simStatus]
  );

  const handleWsMessage = useCallback((msg: any) => {
    if (msg.type === 'tick') {
      setEquity(msg.equity);
      setCash(msg.cash);
      setPositions(msg.positions || []);
      setTickCount(msg.tick);
      const tickPrice = msg.prices ? Object.values(msg.prices as Record<string, number>)[0] : undefined;
      setEquityCurve((prev) => {
        const next = [...prev, { timestamp: msg.timestamp, equity: msg.equity, price: tickPrice }];
        return next.length > 10000 ? next.slice(next.length - 10000) : next;
      });

      if (msg.trade) {
        setTrades((prev) => [
          ...prev,
          {
            timestamp: msg.timestamp,
            symbol: msg.trade.symbol,
            side: msg.trade.side,
            quantity: msg.trade.quantity,
            price: msg.trade.price,
            fee: msg.trade.fee ?? 0,
            pnl: msg.trade.pnl,
          },
        ]);
      }
    } else if (msg.type === 'stopped') {
      setSimStatus(msg.status === 'completed' ? 'completed' : 'stopped');
      // Update final equity/cash from the stopped message
      if (msg.equity !== undefined) setEquity(msg.equity);
      if (msg.cash !== undefined) setCash(msg.cash);
    }
  }, []);

  const { isConnected, send } = useWebSocket(wsUrl, handleWsMessage);

  const handleStop = useCallback(async () => {
    try {
      await apiFetch(`/api/simulation/${simulationId}/stop`, { method: 'POST' });
      setSimStatus('stopped');
    } catch { /* ignore */ }
  }, [simulationId]);

  const handleDelete = useCallback(async () => {
    try {
      await apiFetch(`/api/simulations/${simulationId}`, { method: 'DELETE' });
      router.push('/');
    } catch { /* ignore */ }
  }, [simulationId, router]);

  const handlePause = useCallback(() => { send({ type: 'pause' }); setPaused(true); }, [send]);
  const handleResume = useCallback(() => { send({ type: 'resume' }); setPaused(false); }, [send]);
  const handleSpeedChange = useCallback(
    (s: number) => { send({ type: 'set_speed', speed: s }); setSpeed(s); },
    [send]
  );

  // Compute metrics from equity curve + trades (works for both live and stored data)
  const liveMetrics = useMemo<BacktestMetrics | null>(() => {
    if (equityCurve.length > 0) {
      return computeLiveMetrics(equityCurve, trades, initialCash);
    }
    if (trades.length > 0) {
      return computeLiveMetrics([], trades, initialCash);
    }
    return null;
  }, [equityCurve, trades, initialCash]);

  if (loading) {
    return <p className="text-muted-foreground">Loading...</p>;
  }

  if (fetchError) {
    return (
      <div className="space-y-4">
        <Button variant="outline" onClick={() => router.back()}>Back</Button>
        <p className="text-red-500">{fetchError}</p>
      </div>
    );
  }

  const isRunning = simStatus === 'running';
  const strategyName = detail?.strategy_name ?? '';
  const symbols = detail?.symbols ?? [];
  const mode = detail?.mode ?? '';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="outline" size="sm" onClick={() => router.back()}>
          Back
        </Button>
        <h1 className="text-3xl font-bold">Simulation Detail</h1>
        {!isRunning && (
          <Button variant="destructive" size="sm" className="ml-auto" onClick={handleDelete}>
            Delete
          </Button>
        )}
        <Badge
          variant={
            simStatus === 'running' ? 'default'
            : simStatus === 'completed' ? 'secondary'
            : 'outline'
          }
        >
          {simStatus}
        </Badge>
      </div>

      {/* Config info */}
      <div className="flex flex-wrap gap-x-6 gap-y-1 text-sm text-muted-foreground">
        <span>Strategy: <span className="text-foreground font-medium">{strategyName}</span></span>
        <span>Symbols: <span className="text-foreground font-medium">{symbols.join(', ')}</span></span>
        <span>Mode: <span className="text-foreground font-medium">{mode}</span></span>
        {detail?.interval && (
          <span>Interval: <span className="text-foreground font-medium">{detail.interval}</span></span>
        )}
        <span>Cash: <span className="text-foreground font-medium">${initialCash.toLocaleString()}</span></span>
        {detail?.started_at && (
          <span>Started: <span className="text-foreground font-medium">{new Date(detail.started_at).toLocaleString()}</span></span>
        )}
        {detail?.stopped_at && (
          <span>Stopped: <span className="text-foreground font-medium">{new Date(detail.stopped_at).toLocaleString()}</span></span>
        )}
      </div>

      {/* Playback controls — shown for running simulations */}
      {isRunning && (
        <Card>
          <CardContent className="py-3">
            <SimulationControls
              status={simStatus as any}
              speed={speed}
              tickCount={tickCount}
              isConnected={isConnected}
              paused={paused}
              onStart={() => {}}
              onStop={handleStop}
              onSpeedChange={handleSpeedChange}
              onPause={handlePause}
              onResume={handleResume}
            />
          </CardContent>
        </Card>
      )}

      {detail?.error_message && (
        <Card className="border-red-500">
          <CardContent className="py-3">
            <p className="text-sm text-red-500">{detail.error_message}</p>
          </CardContent>
        </Card>
      )}

      {/* Metrics cards */}
      {liveMetrics && (
        <BacktestResults metrics={liveMetrics} durationMs={0} live />
      )}

      {/* Equity curve — shown for live and stored data */}
      {equityCurve.length > 0 && (
        <LiveChart equityCurve={equityCurve} trades={trades} />
      )}

      {/* Positions — shown for running simulations */}
      {isRunning && (
        <PortfolioDashboard equity={equity} cash={cash} positions={positions} />
      )}

      {/* Trade log */}
      <TradeLog trades={trades} />
    </div>
  );
}
