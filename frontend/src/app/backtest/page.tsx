'use client';

import { useEffect, useCallback } from 'react';
import ConfigurationCard from '@/components/ConfigurationCard';
import BacktestResults from '@/components/BacktestResults';
import BacktestChart from '@/components/BacktestChart';
import TradeLog from '@/components/TradeLog';
import { useBacktestStore } from '@/stores/backtestStore';
import { apiFetch } from '@/lib/api';
import type { StrategyInfo, StrategyParam, BacktestResult } from '@/lib/types';

export default function BacktestPage() {
  const {
    selectedSymbols, setSelectedSymbols,
    strategyName, setStrategyName,
    strategyParams, setStrategyParams,
    dateRange, setDateRange,
    interval, setInterval,
    initialCash, setInitialCash,
    tradingFeePct, setTradingFeePct,
    strategies, setStrategies,
    paramDefs, setParamDefs,
    result, setResult,
    isRunning, setIsRunning,
    error, setError,
  } = useBacktestStore();

  // Fetch strategies on mount
  useEffect(() => {
    apiFetch<StrategyInfo[]>('/api/strategies').then(setStrategies).catch(() => {});
  }, [setStrategies]);

  // Fetch params when strategy changes
  useEffect(() => {
    if (!strategyName) { setParamDefs([]); return; }
    apiFetch<StrategyParam[]>(`/api/strategies/${strategyName}/params`)
      .then((defs) => {
        setParamDefs(defs);
        const defaults: Record<string, number | string> = {};
        defs.forEach((d) => { defaults[d.name] = d.default; });
        setStrategyParams(defaults);
      })
      .catch(() => setParamDefs([]));
  }, [strategyName, setParamDefs, setStrategyParams]);

  const handleParamChange = useCallback(
    (key: string, value: number | string) => {
      setStrategyParams({ ...strategyParams, [key]: value });
    },
    [strategyParams, setStrategyParams]
  );

  const handleSubmit = useCallback(async () => {
    setIsRunning(true);
    setError(null);
    setResult(null);
    try {
      const res = await apiFetch<BacktestResult>('/api/backtest', {
        method: 'POST',
        body: JSON.stringify({
          symbols: selectedSymbols,
          strategy_name: strategyName,
          params: strategyParams,
          start_date: dateRange.start,
          end_date: dateRange.end,
          interval,
          initial_cash: initialCash,
          trading_fee_pct: tradingFeePct,
        }),
      });
      setResult(res);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setIsRunning(false);
    }
  }, [selectedSymbols, strategyName, strategyParams, dateRange, interval, initialCash, tradingFeePct, setResult, setError, setIsRunning]);

  const canSubmit = selectedSymbols.length > 0 && strategyName !== '';

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Backtest</h1>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <ConfigurationCard
            mode="backtest"
            strategies={strategies}
            selectedSymbols={selectedSymbols}
            onSymbolsChange={setSelectedSymbols}
            strategyName={strategyName}
            onStrategyChange={setStrategyName}
            paramDefs={paramDefs}
            strategyParams={strategyParams}
            onParamChange={handleParamChange}
            interval={interval}
            onIntervalChange={setInterval}
            initialCash={initialCash}
            onInitialCashChange={setInitialCash}
            tradingFeePct={tradingFeePct}
            onTradingFeePctChange={setTradingFeePct}
            dateRange={dateRange}
            onDateRangeChange={setDateRange}
            onSubmit={handleSubmit}
            submitLabel="Run Backtest"
            isSubmitting={isRunning}
            canSubmit={canSubmit}
            error={error}
          />
        </div>

        <div className="lg:col-span-2 space-y-6">
          {result && (
            <>
              <BacktestResults metrics={result.metrics} durationMs={result.duration_ms} />
              <BacktestChart equityCurve={result.equity_curve} trades={result.trades as any} />
              <TradeLog trades={result.trades as any} />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
