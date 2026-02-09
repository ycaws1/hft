'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { createChart, LineSeries, createSeriesMarkers, type IChartApi, type ISeriesApi, ColorType } from 'lightweight-charts';
import ChartLegend from '@/components/ChartLegend';
import type { EquityCurvePoint, Trade } from '@/lib/types';

interface BacktestChartProps {
  equityCurve: EquityCurvePoint[];
  trades: Trade[];
}

const EQUITY_COLOR = '#2962FF';
const PRICE_COLOR = '#FF9800';

export default function BacktestChart({ equityCurve, trades }: BacktestChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const equitySeriesRef = useRef<ISeriesApi<'Line'> | null>(null);
  const priceSeriesRef = useRef<ISeriesApi<'Line'> | null>(null);

  const [visibility, setVisibility] = useState({ equity: true, price: true });
  const hasPriceData = equityCurve.some((pt) => pt.price != null);

  // Init chart once
  useEffect(() => {
    if (!containerRef.current) return;

    const chart = createChart(containerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: '#999',
      },
      grid: {
        vertLines: { color: '#1a1a2e' },
        horzLines: { color: '#1a1a2e' },
      },
      width: containerRef.current.clientWidth,
      height: 350,
      timeScale: { timeVisible: true, secondsVisible: true },
      rightPriceScale: { borderColor: '#1a1a2e' },
      leftPriceScale: { visible: true, borderColor: '#1a1a2e' },
    });
    chartRef.current = chart;

    const equitySeries = chart.addSeries(LineSeries, {
      color: EQUITY_COLOR,
      lineWidth: 2,
      title: 'Equity',
    });
    equitySeriesRef.current = equitySeries;

    const priceSeries = chart.addSeries(LineSeries, {
      color: PRICE_COLOR,
      lineWidth: 2,
      title: 'Price',
      priceScaleId: 'left',
    });
    priceSeriesRef.current = priceSeries;

    createSeriesMarkers(equitySeries, []);

    const handleResize = () => {
      if (containerRef.current) {
        chart.applyOptions({ width: containerRef.current.clientWidth });
      }
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
      chartRef.current = null;
      equitySeriesRef.current = null;
      priceSeriesRef.current = null;
    };
  }, []);

  // Update data
  useEffect(() => {
    if (!equitySeriesRef.current || equityCurve.length === 0) return;

    const toTime = (ts: string) =>
      Math.floor(new Date(ts).getTime() / 1000) as unknown as string;

    equitySeriesRef.current.setData(
      equityCurve.map((pt) => ({ time: toTime(pt.timestamp), value: pt.equity })) as any
    );

    if (priceSeriesRef.current) {
      const priceData = equityCurve
        .filter((pt) => pt.price != null)
        .map((pt) => ({ time: toTime(pt.timestamp), value: pt.price! }));
      priceSeriesRef.current.setData(priceData as any);

      if (priceData.length === 0) {
        chartRef.current?.applyOptions({ leftPriceScale: { visible: false } });
      }
    }

    // Trade markers
    const markers = trades.map((t) => ({
      time: toTime(t.timestamp),
      position: t.side === 'BUY' ? ('belowBar' as const) : ('aboveBar' as const),
      color: t.side === 'BUY' ? '#26a69a' : '#ef5350',
      shape: t.side === 'BUY' ? ('arrowUp' as const) : ('arrowDown' as const),
      text: `${t.side} ${t.quantity}`,
    }));
    createSeriesMarkers(equitySeriesRef.current, markers as any);

    chartRef.current?.timeScale().fitContent();
  }, [equityCurve, trades]);

  // Apply visibility changes
  useEffect(() => {
    equitySeriesRef.current?.applyOptions({ visible: visibility.equity });
    priceSeriesRef.current?.applyOptions({ visible: visibility.price });
    chartRef.current?.applyOptions({
      leftPriceScale: { visible: visibility.price && hasPriceData },
    });
  }, [visibility, hasPriceData]);

  const handleToggle = useCallback((key: string) => {
    setVisibility((prev) => ({ ...prev, [key]: !prev[key as keyof typeof prev] }));
  }, []);

  const legendItems = [
    { key: 'equity', label: 'Equity', color: EQUITY_COLOR, visible: visibility.equity },
    ...(hasPriceData
      ? [{ key: 'price', label: 'Price', color: PRICE_COLOR, visible: visibility.price }]
      : []),
  ];

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Equity & Price</h3>
        <ChartLegend items={legendItems} onToggle={handleToggle} />
      </div>
      <div ref={containerRef} className="rounded-md border" />
    </div>
  );
}
