'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { Portfolio } from '@/lib/types';

interface PortfolioDashboardProps {
  equity: number;
  cash: number;
  positions: Portfolio['positions'];
}

export default function PortfolioDashboard({ equity, cash, positions }: PortfolioDashboardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Portfolio</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-6 text-sm">
          <div>
            <span className="text-muted-foreground">Equity: </span>
            <span className="font-medium">${equity.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
          </div>
          <div>
            <span className="text-muted-foreground">Cash: </span>
            <span className="font-medium">${cash.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
          </div>
        </div>

        {positions.length > 0 && (
          <div className="rounded-md border overflow-auto">
            <table className="w-full text-sm">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left px-3 py-2">Symbol</th>
                  <th className="text-right px-3 py-2">Qty</th>
                  <th className="text-right px-3 py-2">Avg Price</th>
                  <th className="text-right px-3 py-2">Unrealized P&L</th>
                </tr>
              </thead>
              <tbody>
                {positions.map((p) => (
                  <tr key={p.symbol} className="border-t">
                    <td className="px-3 py-1.5 font-medium">{p.symbol}</td>
                    <td className="px-3 py-1.5 text-right">{p.quantity}</td>
                    <td className="px-3 py-1.5 text-right">${p.avg_price.toFixed(2)}</td>
                    <td className={`px-3 py-1.5 text-right font-medium ${
                      p.unrealized_pnl >= 0 ? 'text-green-500' : 'text-red-500'
                    }`}>
                      ${p.unrealized_pnl.toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {positions.length === 0 && (
          <p className="text-sm text-muted-foreground">No open positions</p>
        )}
      </CardContent>
    </Card>
  );
}
