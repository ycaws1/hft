import time
import uuid

import pandas as pd

from app.data.provider import DataProvider
from app.engine.metrics import compute_metrics
from app.models.domain import BacktestRequest, BacktestResult, Order, OrderSide
from app.simulation.broker import SimulatedBroker
from app.strategies.base import Strategy


class BacktestEngine:
    def __init__(self, data_provider: DataProvider):
        self.data_provider = data_provider

    async def run(self, request: BacktestRequest, strategy: Strategy) -> BacktestResult:
        start_time = time.time()
        run_id = str(uuid.uuid4())

        # 1. Fetch historical data
        from datetime import datetime

        start_dt = datetime.combine(request.start_date, datetime.min.time())
        end_dt = datetime.combine(request.end_date, datetime.min.time())
        bars = await self.data_provider.get_historical(
            request.symbols[0], start_dt, end_dt, request.interval
        )

        if not bars:
            return self._empty_result(run_id, request.initial_cash)

        df = pd.DataFrame([b.model_dump() for b in bars])

        # Handle pairs trading: fetch second symbol
        if len(request.symbols) > 1 and strategy.name == "pairs_trading":
            bars2 = await self.data_provider.get_historical(
                request.symbols[1], start_dt, end_dt, request.interval
            )
            if bars2:
                df2 = pd.DataFrame([b.model_dump() for b in bars2])
                df["close_2"] = df2["close"].values[: len(df)]

        # 2. Generate signals
        params = strategy.validate_params(request.params)
        df = strategy.generate_signals(df, params)

        # 3. Simulate trades
        broker = SimulatedBroker(
            initial_cash=request.initial_cash,
            fee_pct=request.trading_fee_pct,
        )
        equity_curve = []
        position_size_pct = 0.1  # Use 10% of cash per trade
        symbol = request.symbols[0]

        for i, row in df.iterrows():
            ts = row["timestamp"]
            price = row["close"]
            current_prices = {symbol: price}

            signal = row.get("signal", 0)
            pos = broker.portfolio.positions.get(symbol)
            has_position = pos and pos["quantity"] > 0

            if signal == 1 and not has_position:
                # Buy only when not already holding
                cash_to_use = broker.portfolio.cash * position_size_pct
                qty = int(cash_to_use / price) if price > 0 else 0
                if qty > 0:
                    broker.submit_order(
                        Order(symbol=symbol, side=OrderSide.BUY, quantity=qty),
                        price, ts,
                    )
            elif signal == -1 and has_position:
                # Sell only when holding a position
                broker.submit_order(
                    Order(symbol=symbol, side=OrderSide.SELL, quantity=pos["quantity"]),
                    price, ts,
                )

            equity = broker.portfolio.get_equity(current_prices)
            equity_curve.append({
                "timestamp": ts.isoformat() if hasattr(ts, "isoformat") else str(ts),
                "equity": round(equity, 2),
                "price": round(float(price), 4),
            })

        # 4. Compute metrics
        metrics = compute_metrics(equity_curve, broker.fills, request.initial_cash)

        # 5. Collect trades
        trades = [
            {
                "timestamp": f.timestamp.isoformat() if hasattr(f.timestamp, "isoformat") else str(f.timestamp),
                "symbol": f.symbol,
                "side": f.side.value,
                "quantity": f.quantity,
                "price": round(f.price, 4),
                "fee": round(f.fee, 2),
                "pnl": round(f.pnl, 2) if f.pnl is not None else None,
            }
            for f in broker.fills
        ]

        # 6. Collect indicator data for charts
        indicator_data = {}
        indicator_columns = [c for c in df.columns if c not in [
            "timestamp", "open", "high", "low", "close", "volume", "signal", "close_2"
        ]]
        for col in indicator_columns:
            indicator_data[col] = [
                {
                    "timestamp": row["timestamp"].isoformat()
                    if hasattr(row["timestamp"], "isoformat")
                    else str(row["timestamp"]),
                    "value": round(float(row[col]), 4) if pd.notna(row[col]) else None,
                }
                for _, row in df.iterrows()
            ]

        duration_ms = int((time.time() - start_time) * 1000)

        return BacktestResult(
            id=run_id,
            metrics=metrics,
            equity_curve=equity_curve,
            trades=trades,
            indicator_data=indicator_data,
            duration_ms=duration_ms,
        )

    def _empty_result(self, run_id: str, initial_cash: float) -> BacktestResult:
        from app.models.domain import BacktestMetrics

        return BacktestResult(
            id=run_id,
            metrics=BacktestMetrics(
                total_pnl=0, return_pct=0, sharpe_ratio=0, max_drawdown_pct=0,
                win_rate=0, profit_factor=0, total_trades=0, avg_trade_duration_days=0,
            ),
            equity_curve=[],
            trades=[],
            indicator_data={},
            duration_ms=0,
        )
