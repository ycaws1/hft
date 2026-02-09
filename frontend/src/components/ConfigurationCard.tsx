'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import StockSearch from '@/components/StockSearch';
import StrategySelector from '@/components/StrategySelector';
import ParameterForm from '@/components/ParameterForm';
import type { StrategyInfo, StrategyParam } from '@/lib/types';

interface ConfigurationCardProps {
  mode: 'backtest' | 'simulation';

  // Shared fields
  strategies: StrategyInfo[];
  selectedSymbols: string[];
  onSymbolsChange: (symbols: string[]) => void;
  strategyName: string;
  onStrategyChange: (name: string) => void;
  paramDefs: StrategyParam[];
  strategyParams: Record<string, number | string>;
  onParamChange: (key: string, value: number | string) => void;
  interval: string;
  onIntervalChange: (interval: string) => void;
  initialCash: number;
  onInitialCashChange: (cash: number) => void;
  tradingFeePct: number;
  onTradingFeePctChange: (fee: number) => void;

  // Backtest-specific
  dateRange?: { start: string; end: string };
  onDateRangeChange?: (range: { start: string; end: string }) => void;

  // Simulation-specific
  simMode?: 'replay' | 'realtime';
  onSimModeChange?: (mode: 'replay' | 'realtime') => void;
  speed?: number;
  onSpeedChange?: (speed: number) => void;

  // Action
  onSubmit: () => void;
  submitLabel: string;
  isSubmitting: boolean;
  canSubmit: boolean;
  error?: string | null;
}

export default function ConfigurationCard({
  mode,
  strategies,
  selectedSymbols,
  onSymbolsChange,
  strategyName,
  onStrategyChange,
  paramDefs,
  strategyParams,
  onParamChange,
  interval,
  onIntervalChange,
  initialCash,
  onInitialCashChange,
  tradingFeePct,
  onTradingFeePctChange,
  dateRange,
  onDateRangeChange,
  simMode,
  onSimModeChange,
  speed,
  onSpeedChange,
  onSubmit,
  submitLabel,
  isSubmitting,
  canSubmit,
  error,
}: ConfigurationCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>
          {mode === 'backtest' ? 'Backtest Configuration' : 'Simulation Configuration'}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Stock selection */}
        <StockSearch selected={selectedSymbols} onChange={onSymbolsChange} />

        {/* Strategy selection */}
        <StrategySelector
          strategies={strategies}
          value={strategyName}
          onChange={onStrategyChange}
        />

        {/* Strategy parameters */}
        <ParameterForm
          paramDefs={paramDefs}
          values={strategyParams}
          onChange={onParamChange}
        />

        {/* Date range - backtest always, simulation in replay mode */}
        {dateRange && onDateRangeChange && (mode === 'backtest' || simMode === 'replay') && (
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-sm font-medium">Start Date</label>
              <Input
                type="date"
                value={dateRange.start}
                onChange={(e) =>
                  onDateRangeChange({ ...dateRange, start: e.target.value })
                }
              />
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium">End Date</label>
              <Input
                type="date"
                value={dateRange.end}
                onChange={(e) =>
                  onDateRangeChange({ ...dateRange, end: e.target.value })
                }
              />
            </div>
          </div>
        )}

        {/* Simulation mode - simulation only */}
        {mode === 'simulation' && onSimModeChange && (
          <div className="space-y-1">
            <label className="text-sm font-medium">Mode</label>
            <Select
              value={simMode}
              onValueChange={(v) => onSimModeChange(v as 'replay' | 'realtime')}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="replay">Replay (Historical)</SelectItem>
                <SelectItem value="realtime">Real-time</SelectItem>
              </SelectContent>
            </Select>
          </div>
        )}

        {/* Interval, Initial Cash, Fee - shared row */}
        <div className="grid grid-cols-3 gap-3">
          <div className="space-y-1">
            <label className="text-sm font-medium">Interval</label>
            <Select value={interval} onValueChange={onIntervalChange}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1h">Hourly</SelectItem>
                <SelectItem value="1d">Daily</SelectItem>
                <SelectItem value="1wk">Weekly</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1">
            <label className="text-sm font-medium">Initial Cash</label>
            <Input
              type="number"
              value={initialCash}
              onChange={(e) => onInitialCashChange(Number(e.target.value))}
            />
          </div>
          <div className="space-y-1">
            <label className="text-sm font-medium">Fee (%)</label>
            <Input
              type="number"
              step="0.1"
              min="0"
              max="10"
              value={tradingFeePct}
              onChange={(e) => onTradingFeePctChange(Number(e.target.value))}
            />
          </div>
        </div>

        {/* Speed slider - simulation only */}
        {mode === 'simulation' && speed !== undefined && onSpeedChange && (
          <div className="space-y-1">
            <label className="text-sm font-medium">Speed</label>
            <div className="flex items-center gap-2 mt-2">
              <Slider
                className="flex-1"
                min={1}
                max={50}
                step={1}
                value={[speed]}
                onValueChange={([v]) => onSpeedChange(v)}
              />
              <div className="flex items-center gap-1">
                <Input
                  type="number"
                  className="w-16 h-8 text-xs text-center"
                  min={1}
                  max={50}
                  step={1}
                  value={speed}
                  onChange={(e) => {
                    const v = parseInt(e.target.value);
                    if (!isNaN(v)) onSpeedChange(Math.min(50, Math.max(1, v)));
                  }}
                />
                <span className="text-xs text-muted-foreground">x</span>
              </div>
            </div>
          </div>
        )}

        {/* Submit button */}
        <Button
          className="w-full"
          onClick={onSubmit}
          disabled={!canSubmit || isSubmitting}
        >
          {isSubmitting ? 'Running...' : submitLabel}
        </Button>

        {error && (
          <p className="text-sm text-red-500">{error}</p>
        )}
      </CardContent>
    </Card>
  );
}
