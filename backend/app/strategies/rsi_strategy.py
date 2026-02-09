import pandas as pd

from app.indicators.rsi import compute_rsi
from app.models.domain import StrategyParamDef
from app.strategies.base import Strategy


class RSIStrategy(Strategy):
    @property
    def name(self) -> str:
        return "rsi"

    @property
    def display_name(self) -> str:
        return "RSI Overbought/Oversold"

    @property
    def description(self) -> str:
        return "Buy when RSI crosses below oversold level, sell when above overbought."

    @property
    def category(self) -> str:
        return "technical"

    def parameters(self) -> list[StrategyParamDef]:
        return [
            StrategyParamDef(name="period", label="RSI Period", type="int", default=14, min=2, max=50),
            StrategyParamDef(name="overbought", label="Overbought", type="int", default=70, min=50, max=95),
            StrategyParamDef(name="oversold", label="Oversold", type="int", default=30, min=5, max=50),
        ]

    def generate_signals(self, data: pd.DataFrame, params: dict) -> pd.DataFrame:
        params = self.validate_params(params)
        data["rsi"] = compute_rsi(data["close"], params["period"])

        data["signal"] = 0
        prev_rsi = data["rsi"].shift(1)
        # Buy: RSI crosses above oversold from below
        data.loc[(prev_rsi <= params["oversold"]) & (data["rsi"] > params["oversold"]), "signal"] = 1
        # Sell: RSI crosses below overbought from above
        data.loc[(prev_rsi >= params["overbought"]) & (data["rsi"] < params["overbought"]), "signal"] = -1
        return data
