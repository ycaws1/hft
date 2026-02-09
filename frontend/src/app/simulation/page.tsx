'use client';

import { useEffect, useCallback, useState } from 'react';
import { useRouter } from 'next/navigation';
import ConfigurationCard from '@/components/ConfigurationCard';
import { useSimulationStore } from '@/stores/simulationStore';
import { apiFetch } from '@/lib/api';
import type { StrategyInfo, StrategyParam } from '@/lib/types';

export default function SimulationPage() {
  const router = useRouter();
  const {
    selectedSymbols, setSelectedSymbols,
    strategyName, setStrategyName,
    strategyParams, setStrategyParams,
    simMode, setSimMode,
    dateRange, setDateRange,
    interval, setInterval,
    initialCash, setInitialCash,
    tradingFeePct, setTradingFeePct,
    speed, setSpeed,
    strategies, setStrategies,
    paramDefs, setParamDefs,
    error, setError,
    reset,
  } = useSimulationStore();

  const [isSubmitting, setIsSubmitting] = useState(false);

  // Reset store on mount so navbar always opens a fresh config
  useEffect(() => { reset(); }, [reset]);

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
    setIsSubmitting(true);
    setError(null);
    try {
      const simConfig: Record<string, unknown> = {
        strategy_name: strategyName,
        params: strategyParams,
        symbols: selectedSymbols,
        mode: simMode,
        speed,
        interval,
        initial_cash: initialCash,
        trading_fee_pct: tradingFeePct,
      };
      if (simMode === 'replay') {
        simConfig.start_date = dateRange.start;
        simConfig.end_date = dateRange.end;
      }

      const result = await apiFetch<{ simulation_id: string; status: string }>(
        '/api/simulation',
        { method: 'POST', body: JSON.stringify(simConfig) }
      );
      router.push(`/simulation/${result.simulation_id}`);
    } catch (e: any) {
      setError(e.message);
      setIsSubmitting(false);
    }
  }, [selectedSymbols, strategyName, strategyParams, simMode, dateRange, interval, initialCash, tradingFeePct, speed, setError, router]);

  const canSubmit = selectedSymbols.length > 0 && strategyName !== '';

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Simulation</h1>
      <div className="max-w-lg">
        <ConfigurationCard
          mode="simulation"
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
          simMode={simMode}
          onSimModeChange={setSimMode}
          speed={speed}
          onSpeedChange={setSpeed}
          onSubmit={handleSubmit}
          submitLabel="Start Simulation"
          isSubmitting={isSubmitting}
          canSubmit={canSubmit}
          error={error}
        />
      </div>
    </div>
  );
}
