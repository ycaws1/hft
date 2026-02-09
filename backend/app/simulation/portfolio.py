from datetime import datetime

from app.models.domain import Position, PortfolioSnapshot


class Portfolio:
    def __init__(self, cash: float = 100000.0):
        self.cash = cash
        self.initial_cash = cash
        self.positions: dict[str, dict] = {}  # symbol -> {quantity, avg_price}

    def update_position(self, symbol: str, quantity: float, price: float) -> None:
        if symbol in self.positions:
            pos = self.positions[symbol]
            if quantity > 0:  # buying more
                total_cost = pos["avg_price"] * pos["quantity"] + price * quantity
                pos["quantity"] += quantity
                pos["avg_price"] = total_cost / pos["quantity"] if pos["quantity"] != 0 else 0
            else:  # selling
                pos["quantity"] += quantity  # quantity is negative for sells
            if abs(pos["quantity"]) < 1e-8:
                del self.positions[symbol]
        else:
            if quantity > 0:
                self.positions[symbol] = {"quantity": quantity, "avg_price": price}

    def get_equity(self, current_prices: dict[str, float]) -> float:
        position_value = sum(
            pos["quantity"] * current_prices.get(sym, pos["avg_price"])
            for sym, pos in self.positions.items()
        )
        return self.cash + position_value

    def snapshot(self, timestamp: datetime, current_prices: dict[str, float]) -> PortfolioSnapshot:
        positions = []
        for sym, pos in self.positions.items():
            current_price = current_prices.get(sym, pos["avg_price"])
            unrealized = (current_price - pos["avg_price"]) * pos["quantity"]
            positions.append(
                Position(
                    symbol=sym,
                    quantity=pos["quantity"],
                    avg_price=pos["avg_price"],
                    unrealized_pnl=unrealized,
                )
            )
        return PortfolioSnapshot(
            timestamp=timestamp,
            cash=self.cash,
            total_equity=self.get_equity(current_prices),
            positions=positions,
        )

    def to_dict(self, current_prices: dict[str, float]) -> dict:
        snap = self.snapshot(datetime.now(), current_prices)
        return snap.model_dump()
