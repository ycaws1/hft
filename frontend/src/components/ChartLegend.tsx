'use client';

interface LegendItem {
  key: string;
  label: string;
  color: string;
  visible: boolean;
}

interface ChartLegendProps {
  items: LegendItem[];
  onToggle: (key: string) => void;
}

export default function ChartLegend({ items, onToggle }: ChartLegendProps) {
  return (
    <div className="flex items-center gap-3">
      {items.map((item) => (
        <button
          key={item.key}
          onClick={() => onToggle(item.key)}
          className={`flex items-center gap-1.5 text-xs transition-opacity ${
            item.visible ? 'opacity-100' : 'opacity-40'
          }`}
        >
          <span
            className="inline-block w-3 h-3 rounded-sm"
            style={{ backgroundColor: item.color }}
          />
          <span className={item.visible ? '' : 'line-through'}>{item.label}</span>
        </button>
      ))}
    </div>
  );
}
