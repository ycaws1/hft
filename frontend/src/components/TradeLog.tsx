'use client';

import type { Trade } from '@/lib/types';

interface TradeLogProps {
  trades: Trade[];
}

export default function TradeLog({ trades }: TradeLogProps) {
  if (trades.length === 0) return null;

  return (
    <div className="space-y-2">
      <h3 className="text-lg font-semibold">Trade Log</h3>
      <div className="rounded-md border overflow-auto max-h-96">
        <table className="w-full text-sm">
          <thead className="bg-muted/50 sticky top-0">
            <tr>
              <th className="text-left px-3 py-2">Time</th>
              <th className="text-left px-3 py-2">Symbol</th>
              <th className="text-left px-3 py-2">Side</th>
              <th className="text-right px-3 py-2">Qty</th>
              <th className="text-right px-3 py-2">Price</th>
              <th className="text-right px-3 py-2">Fee</th>
              <th className="text-right px-3 py-2">P&L</th>
            </tr>
          </thead>
          <tbody>
            {[...trades].reverse().map((t, i) => (
              <tr key={i} className="border-t">
                <td className="px-3 py-1.5 text-xs text-muted-foreground">
                  {new Date(t.timestamp).toLocaleString()}
                </td>
                <td className="px-3 py-1.5">{t.symbol}</td>
                <td className={`px-3 py-1.5 font-medium ${t.side === 'BUY' ? 'text-green-500' : 'text-red-500'}`}>
                  {t.side}
                </td>
                <td className="px-3 py-1.5 text-right">{t.quantity}</td>
                <td className="px-3 py-1.5 text-right">${t.price.toFixed(2)}</td>
                <td className="px-3 py-1.5 text-right text-muted-foreground">${t.fee.toFixed(2)}</td>
                <td className={`px-3 py-1.5 text-right font-medium ${
                  t.pnl == null ? '' : t.pnl >= 0 ? 'text-green-500' : 'text-red-500'
                }`}>
                  {t.pnl != null ? `$${t.pnl.toFixed(2)}` : '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
