import pandas as pd

from app.indicators.moving_average import compute_ema, compute_sma
from app.models.domain import StrategyParamDef
from app.strategies.base import Strategy


class MACrossoverStrategy(Strategy):
    @property
    def name(self) -> str:
        return "ma_crossover"

    @property
    def display_name(self) -> str:
        return "Moving Average Crossover"

    @property
    def description(self) -> str:
        return "Buy when fast MA crosses above slow MA, sell when it crosses below."

    @property
    def category(self) -> str:
        return "technical"

    def parameters(self) -> list[StrategyParamDef]:
        return [
            StrategyParamDef(name="fast_period", label="Fast Period", type="int", default=10, min=2, max=100),
            StrategyParamDef(name="slow_period", label="Slow Period", type="int", default=30, min=5, max=200),
            StrategyParamDef(name="ma_type", label="MA Type", type="select", default="SMA", options=["SMA", "EMA"]),
        ]

    def generate_signals(self, data: pd.DataFrame, params: dict) -> pd.DataFrame:
        params = self.validate_params(params)
        close = data["close"]
        ma_fn = compute_sma if params["ma_type"] == "SMA" else compute_ema

        data["sma_fast"] = ma_fn(close, params["fast_period"])
        data["sma_slow"] = ma_fn(close, params["slow_period"])

        data["signal"] = 0
        data.loc[data["sma_fast"] > data["sma_slow"], "signal"] = 1
        data.loc[data["sma_fast"] <= data["sma_slow"], "signal"] = -1

        # Only generate signals on crossover (change in position)
        data["signal"] = data["signal"].diff().fillna(0).apply(
            lambda x: 1 if x > 0 else (-1 if x < 0 else 0)
        )
        return data
