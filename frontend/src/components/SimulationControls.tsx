'use client';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';

interface SimulationControlsProps {
  status: string;
  speed: number;
  tickCount: number;
  isConnected: boolean;
  paused?: boolean;
  onStart: () => void;
  onStop: () => void;
  onSpeedChange: (speed: number) => void;
  onPause: () => void;
  onResume: () => void;
}

export default function SimulationControls({
  status,
  speed,
  tickCount,
  isConnected,
  paused,
  onStart,
  onStop,
  onSpeedChange,
  onPause,
  onResume,
}: SimulationControlsProps) {
  const statusColor = {
    idle: 'bg-gray-500',
    running: 'bg-green-500',
    stopped: 'bg-yellow-500',
    completed: 'bg-blue-500',
    error: 'bg-red-500',
  }[status] || 'bg-gray-500';

  return (
    <div className="flex items-center gap-4 flex-wrap">
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${statusColor}`} />
        <span className="text-sm font-medium capitalize">{status}</span>
      </div>

      {isConnected && (
        <Badge variant="outline" className="text-xs">
          WS Connected
        </Badge>
      )}

      <span className="text-xs text-muted-foreground">Tick #{tickCount}</span>

      <div className="flex items-center gap-2">
        {status === 'idle' && (
          <Button size="sm" onClick={onStart}>
            Start
          </Button>
        )}
        {status === 'running' && !paused && (
          <>
            <Button size="sm" variant="outline" onClick={onPause}>
              Pause
            </Button>
            <Button size="sm" variant="destructive" onClick={onStop}>
              Stop
            </Button>
          </>
        )}
        {status === 'running' && paused && (
          <>
            <Button size="sm" onClick={onResume}>
              Resume
            </Button>
            <Button size="sm" variant="destructive" onClick={onStop}>
              Stop
            </Button>
          </>
        )}
      </div>

      {status === 'running' && (
        <div className="flex items-center gap-2 ml-auto">
          <span className="text-xs text-muted-foreground">Speed:</span>
          <Slider
            className="w-32"
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
      )}
    </div>
  );
}
