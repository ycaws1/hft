import { create } from 'zustand';
import type { BacktestResult, StrategyInfo, StrategyParam } from '@/lib/types';

interface BacktestState {
  // Config
  selectedSymbols: string[];
  strategyName: string;
  strategyParams: Record<string, number | string>;
  dateRange: { start: string; end: string };
  interval: string;
  initialCash: number;
  tradingFeePct: number;

  // Metadata
  strategies: StrategyInfo[];
  paramDefs: StrategyParam[];

  // Result
  result: BacktestResult | null;
  isRunning: boolean;
  error: string | null;

  // Actions
  setSelectedSymbols: (symbols: string[]) => void;
  setStrategyName: (name: string) => void;
  setStrategyParams: (params: Record<string, number | string>) => void;
  setDateRange: (range: { start: string; end: string }) => void;
  setInterval: (interval: string) => void;
  setInitialCash: (cash: number) => void;
  setTradingFeePct: (fee: number) => void;
  setStrategies: (strategies: StrategyInfo[]) => void;
  setParamDefs: (defs: StrategyParam[]) => void;
  setResult: (result: BacktestResult | null) => void;
  setIsRunning: (running: boolean) => void;
  setError: (error: string | null) => void;
}

export const useBacktestStore = create<BacktestState>((set) => ({
  selectedSymbols: [],
  strategyName: '',
  strategyParams: {},
  dateRange: { start: '2023-01-01', end: '2024-01-01' },
  interval: '1d',
  initialCash: 100000,
  tradingFeePct: 1.0,

  strategies: [],
  paramDefs: [],

  result: null,
  isRunning: false,
  error: null,

  setSelectedSymbols: (symbols) => set({ selectedSymbols: symbols }),
  setStrategyName: (name) => set({ strategyName: name }),
  setStrategyParams: (params) => set({ strategyParams: params }),
  setDateRange: (range) => set({ dateRange: range }),
  setInterval: (interval) => set({ interval }),
  setInitialCash: (cash) => set({ initialCash: cash }),
  setTradingFeePct: (fee) => set({ tradingFeePct: fee }),
  setStrategies: (strategies) => set({ strategies }),
  setParamDefs: (defs) => set({ paramDefs: defs }),
  setResult: (result) => set({ result }),
  setIsRunning: (running) => set({ isRunning: running }),
  setError: (error) => set({ error }),
}));
