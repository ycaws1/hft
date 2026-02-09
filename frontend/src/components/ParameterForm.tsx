'use client';

import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { StrategyParam } from '@/lib/types';

interface ParameterFormProps {
  paramDefs: StrategyParam[];
  values: Record<string, number | string>;
  onChange: (key: string, value: number | string) => void;
}

export default function ParameterForm({
  paramDefs,
  values,
  onChange,
}: ParameterFormProps) {
  if (paramDefs.length === 0) return null;

  return (
    <div className="space-y-4">
      <label className="text-sm font-medium">Parameters</label>
      {paramDefs.map((p) => (
        <div key={p.name} className="space-y-1">
          <div className="flex justify-between">
            <span className="text-sm">{p.label}</span>
            <span className="text-sm text-muted-foreground">
              {values[p.name] ?? p.default}
            </span>
          </div>
          {p.type === 'select' && p.options ? (
            <Select
              value={String(values[p.name] ?? p.default)}
              onValueChange={(v) => onChange(p.name, v)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {p.options.map((opt) => (
                  <SelectItem key={opt} value={opt}>
                    {opt}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          ) : p.min !== undefined && p.max !== undefined ? (
            <div className="flex items-center gap-2">
              <Slider
                className="flex-1"
                min={p.min}
                max={p.max}
                step={p.type === 'int' ? 1 : 0.1}
                value={[Number(values[p.name] ?? p.default)]}
                onValueChange={([v]) => onChange(p.name, p.type === 'int' ? Math.round(v) : v)}
              />
              <Input
                type="number"
                className="w-16 h-8 text-xs text-center"
                min={p.min}
                max={p.max}
                step={p.type === 'int' ? 1 : 0.1}
                value={values[p.name] ?? p.default}
                onChange={(e) => {
                  const raw = p.type === 'int' ? parseInt(e.target.value) : parseFloat(e.target.value);
                  if (!isNaN(raw)) {
                    const clamped = Math.min(p.max!, Math.max(p.min!, raw));
                    onChange(p.name, p.type === 'int' ? Math.round(clamped) : clamped);
                  }
                }}
              />
            </div>
          ) : (
            <Input
              type="number"
              value={values[p.name] ?? p.default}
              onChange={(e) =>
                onChange(
                  p.name,
                  p.type === 'int'
                    ? parseInt(e.target.value) || 0
                    : parseFloat(e.target.value) || 0
                )
              }
            />
          )}
        </div>
      ))}
    </div>
  );
}
