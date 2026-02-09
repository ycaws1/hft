'use client';

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { StrategyInfo } from '@/lib/types';

interface StrategySelectorProps {
  strategies: StrategyInfo[];
  value: string;
  onChange: (name: string) => void;
}

export default function StrategySelector({
  strategies,
  value,
  onChange,
}: StrategySelectorProps) {
  return (
    <div className="space-y-1">
      <label className="text-sm font-medium">Strategy</label>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger>
          <SelectValue placeholder="Select a strategy" />
        </SelectTrigger>
        <SelectContent>
          {strategies.map((s) => (
            <SelectItem key={s.name} value={s.name}>
              {s.display_name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
