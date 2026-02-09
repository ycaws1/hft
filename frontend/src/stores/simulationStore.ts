import { create } from 'zustand';
import type { StrategyInfo, StrategyParam } from '@/lib/types';

interface SimulationState {
  // Config
  selectedSymbols: string[];
  strategyName: string;
  strategyParams: Record<string, number | string>;
  simMode: 'replay' | 'realtime';
  dateRange: { start: string; end: string };
  interval: string;
  initialCash: number;
  tradingFeePct: number;
  speed: number;

  // Metadata
  strategies: StrategyInfo[];
  paramDefs: StrategyParam[];

  // Status
  status: string;
  error: string | null;

  // Actions
  setSelectedSymbols: (symbols: string[]) => void;
  setStrategyName: (name: string) => void;
  setStrategyParams: (params: Record<string, number | string>) => void;
  setSimMode: (mode: 'replay' | 'realtime') => void;
  setDateRange: (range: { start: string; end: string }) => void;
  setInterval: (interval: string) => void;
  setInitialCash: (cash: number) => void;
  setTradingFeePct: (fee: number) => void;
  setSpeed: (speed: number) => void;
  setStrategies: (strategies: StrategyInfo[]) => void;
  setParamDefs: (defs: StrategyParam[]) => void;
  setStatus: (status: string) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const initialState = {
  selectedSymbols: [],
  strategyName: '',
  strategyParams: {},
  simMode: 'replay' as const,
  dateRange: { start: '2023-01-01', end: '2024-01-01' },
  interval: '1d',
  initialCash: 100000,
  tradingFeePct: 1.0,
  speed: 5,
  strategies: [],
  paramDefs: [],
  status: 'idle',
  error: null,
};

export const useSimulationStore = create<SimulationState>((set) => ({
  ...initialState,

  setSelectedSymbols: (symbols) => set({ selectedSymbols: symbols }),
  setStrategyName: (name) => set({ strategyName: name }),
  setStrategyParams: (params) => set({ strategyParams: params }),
  setSimMode: (mode) => set({ simMode: mode }),
  setDateRange: (range) => set({ dateRange: range }),
  setInterval: (interval) => set({ interval }),
  setInitialCash: (cash) => set({ initialCash: cash }),
  setTradingFeePct: (fee) => set({ tradingFeePct: fee }),
  setSpeed: (speed) => set({ speed }),
  setStrategies: (strategies) => set({ strategies }),
  setParamDefs: (defs) => set({ paramDefs: defs }),
  setStatus: (status) => set({ status }),
  setError: (error) => set({ error }),
  reset: () => set(initialState),
}));
