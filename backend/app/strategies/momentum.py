import pandas as pd

from app.models.domain import StrategyParamDef
from app.strategies.base import Strategy


class MomentumStrategy(Strategy):
    @property
    def name(self) -> str:
        return "momentum"

    @property
    def display_name(self) -> str:
        return "Momentum"

    @property
    def description(self) -> str:
        return "Buy when price momentum exceeds threshold, sell when it drops below."

    @property
    def category(self) -> str:
        return "quant"

    def parameters(self) -> list[StrategyParamDef]:
        return [
            StrategyParamDef(name="lookback", label="Lookback Period", type="int", default=20, min=5, max=200),
            StrategyParamDef(name="threshold", label="Momentum Threshold %", type="float", default=5.0, min=0.5, max=30.0),
        ]

    def generate_signals(self, data: pd.DataFrame, params: dict) -> pd.DataFrame:
        params = self.validate_params(params)
        close = data["close"]
        data["momentum_pct"] = close.pct_change(periods=params["lookback"]) * 100

        data["signal"] = 0
        prev_momentum = data["momentum_pct"].shift(1)
        threshold = params["threshold"]
        # Buy when momentum crosses above threshold
        data.loc[(prev_momentum <= threshold) & (data["momentum_pct"] > threshold), "signal"] = 1
        # Sell when momentum crosses below negative threshold
        data.loc[(prev_momentum >= -threshold) & (data["momentum_pct"] < -threshold), "signal"] = -1
        return data
