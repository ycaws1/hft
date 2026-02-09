from app.strategies.base import Strategy


class StrategyRegistry:
    def __init__(self):
        self._strategies: dict[str, Strategy] = {}

    def register(self, strategy: Strategy) -> None:
        self._strategies[strategy.name] = strategy

    def get(self, name: str) -> Strategy:
        if name not in self._strategies:
            raise ValueError(
                f"Strategy '{name}' not found. Available: {list(self._strategies.keys())}"
            )
        return self._strategies[name]

    @property
    def all(self) -> list[Strategy]:
        return list(self._strategies.values())


strategy_registry = StrategyRegistry()


def _register_all():
    from app.strategies.bollinger_strategy import BollingerStrategy
    from app.strategies.ma_crossover import MACrossoverStrategy
    from app.strategies.macd_strategy import MACDStrategy
    from app.strategies.mean_reversion import MeanReversionStrategy
    from app.strategies.momentum import MomentumStrategy
    from app.strategies.pairs_trading import PairsTradingStrategy
    from app.strategies.rsi_strategy import RSIStrategy

    for cls in [
        MACrossoverStrategy,
        RSIStrategy,
        MACDStrategy,
        BollingerStrategy,
        MeanReversionStrategy,
        MomentumStrategy,
        PairsTradingStrategy,
    ]:
        strategy_registry.register(cls())


_register_all()
