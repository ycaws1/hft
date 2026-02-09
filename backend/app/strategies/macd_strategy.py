import pandas as pd

from app.indicators.macd import compute_macd
from app.models.domain import StrategyParamDef
from app.strategies.base import Strategy


class MACDStrategy(Strategy):
    @property
    def name(self) -> str:
        return "macd"

    @property
    def display_name(self) -> str:
        return "MACD Signal Crossover"

    @property
    def description(self) -> str:
        return "Buy when MACD crosses above signal line, sell when it crosses below."

    @property
    def category(self) -> str:
        return "technical"

    def parameters(self) -> list[StrategyParamDef]:
        return [
            StrategyParamDef(name="fast_period", label="Fast EMA Period", type="int", default=12, min=2, max=50),
            StrategyParamDef(name="slow_period", label="Slow EMA Period", type="int", default=26, min=5, max=100),
            StrategyParamDef(name="signal_period", label="Signal Period", type="int", default=9, min=2, max=30),
        ]

    def generate_signals(self, data: pd.DataFrame, params: dict) -> pd.DataFrame:
        params = self.validate_params(params)
        macd_line, signal_line, histogram = compute_macd(
            data["close"], params["fast_period"], params["slow_period"], params["signal_period"]
        )
        data["macd"] = macd_line
        data["macd_signal"] = signal_line
        data["macd_histogram"] = histogram

        data["signal"] = 0
        prev_hist = histogram.shift(1)
        # Buy: histogram crosses from negative to positive
        data.loc[(prev_hist <= 0) & (histogram > 0), "signal"] = 1
        # Sell: histogram crosses from positive to negative
        data.loc[(prev_hist >= 0) & (histogram < 0), "signal"] = -1
        return data
