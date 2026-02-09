'use client';

import { useState, useRef, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { apiFetch } from '@/lib/api';

interface StockSearchResult {
  symbol: string;
  name: string;
  exchange: string;
}

interface StockSearchProps {
  selected: string[];
  onChange: (symbols: string[]) => void;
}

export default function StockSearch({ selected, onChange }: StockSearchProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<StockSearchResult[]>([]);
  const [open, setOpen] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (query.length < 1) {
      setResults([]);
      return;
    }
    clearTimeout(timerRef.current);
    timerRef.current = setTimeout(async () => {
      try {
        const data = await apiFetch<StockSearchResult[]>(
          `/api/stocks/search?q=${encodeURIComponent(query)}`
        );
        setResults(data);
        setOpen(true);
      } catch {
        setResults([]);
      }
    }, 300);
  }, [query]);

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const addSymbol = (symbol: string) => {
    if (!selected.includes(symbol)) {
      onChange([...selected, symbol]);
    }
    setQuery('');
    setOpen(false);
  };

  const removeSymbol = (symbol: string) => {
    onChange(selected.filter((s) => s !== symbol));
  };

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium">Stocks</label>
      <div className="flex flex-wrap gap-1 mb-2">
        {selected.map((sym) => (
          <Badge key={sym} variant="secondary" className="cursor-pointer" onClick={() => removeSymbol(sym)}>
            {sym} ✕
          </Badge>
        ))}
      </div>
      <div ref={containerRef} className="relative">
        <Input
          placeholder="Search stocks..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => results.length > 0 && setOpen(true)}
        />
        {open && results.length > 0 && (
          <ul className="absolute z-50 w-full mt-1 bg-popover border rounded-md shadow-md max-h-60 overflow-auto">
            {results.map((r) => (
              <li
                key={r.symbol}
                className="px-3 py-2 text-sm hover:bg-accent cursor-pointer flex justify-between"
                onClick={() => addSymbol(r.symbol)}
              >
                <span className="font-medium">{r.symbol}</span>
                <span className="text-muted-foreground text-xs truncate ml-2">
                  {r.name} · {r.exchange}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
