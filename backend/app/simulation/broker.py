import uuid
from datetime import datetime

from app.models.domain import Fill, Order, OrderSide
from app.simulation.portfolio import Portfolio


class SimulatedBroker:
    def __init__(
        self,
        initial_cash: float = 100000.0,
        slippage_bps: float = 1.0,
        fee_pct: float = 1.0,
    ):
        self.portfolio = Portfolio(cash=initial_cash)
        self.fills: list[Fill] = []
        self.slippage_bps = slippage_bps
        self.fee_pct = fee_pct  # percentage fee per trade (e.g. 1.0 = 1%)
        self._recent_fills: list[Fill] = []
        self.total_fees: float = 0.0

    def submit_order(self, order: Order, price: float, timestamp: datetime) -> Fill | None:
        """Execute an order immediately at the given price with slippage and fee."""
        pnl = None

        if order.side == OrderSide.BUY:
            exec_price = price * (1 + self.slippage_bps / 10000)
            notional = exec_price * order.quantity
            fee = notional * (self.fee_pct / 100)
            total_cost = notional + fee
            if total_cost > self.portfolio.cash:
                return None  # insufficient funds
            self.portfolio.cash -= total_cost
            # Use fee-inclusive cost per share so unrealized P&L accounts for buy fee
            cost_per_share = total_cost / order.quantity
            self.portfolio.update_position(order.symbol, order.quantity, cost_per_share)
        else:
            exec_price = price * (1 - self.slippage_bps / 10000)
            sym_pos = self.portfolio.positions.get(order.symbol)
            if not sym_pos or sym_pos["quantity"] < order.quantity:
                return None  # insufficient shares
            notional = exec_price * order.quantity
            fee = notional * (self.fee_pct / 100)
            proceeds = notional - fee
            pnl = (exec_price - sym_pos["avg_price"]) * order.quantity - fee
            self.portfolio.cash += proceeds
            self.portfolio.update_position(order.symbol, -order.quantity, exec_price)

        self.total_fees += fee

        fill = Fill(
            timestamp=timestamp,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=exec_price,
            fee=round(fee, 2),
            pnl=pnl if order.side == OrderSide.SELL else None,
            order_id=str(uuid.uuid4()),
        )
        self.fills.append(fill)
        self._recent_fills.append(fill)
        return fill

    def recent_fills(self) -> list[Fill]:
        fills = self._recent_fills[:]
        self._recent_fills.clear()
        return fills

    def get_portfolio(self) -> Portfolio:
        return self.portfolio
