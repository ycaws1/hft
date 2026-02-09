import pandas as pd

from app.models.domain import StrategyParamDef
from app.strategies.base import Strategy


class MeanReversionStrategy(Strategy):
    @property
    def name(self) -> str:
        return "mean_reversion"

    @property
    def display_name(self) -> str:
        return "Mean Reversion"

    @property
    def description(self) -> str:
        return "Buy when price z-score drops below entry threshold, sell when it rises above."

    @property
    def category(self) -> str:
        return "quant"

    def parameters(self) -> list[StrategyParamDef]:
        return [
            StrategyParamDef(name="lookback", label="Lookback Period", type="int", default=20, min=5, max=200),
            StrategyParamDef(name="entry_z", label="Entry Z-Score", type="float", default=-2.0, min=-4.0, max=-0.5),
            StrategyParamDef(name="exit_z", label="Exit Z-Score", type="float", default=0.0, min=-1.0, max=2.0),
        ]

    def generate_signals(self, data: pd.DataFrame, params: dict) -> pd.DataFrame:
        params = self.validate_params(params)
        close = data["close"]
        rolling_mean = close.rolling(window=params["lookback"]).mean()
        rolling_std = close.rolling(window=params["lookback"]).std()
        data["z_score"] = (close - rolling_mean) / rolling_std

        # Raw position: 1 when z-score below entry, -1 when above exit
        raw = pd.Series(0, index=data.index)
        raw[data["z_score"] <= params["entry_z"]] = 1
        raw[data["z_score"] >= params["exit_z"]] = -1

        # Only signal on transitions (crossover)
        data["signal"] = 0
        data.loc[(raw == 1) & (raw.shift(1) != 1), "signal"] = 1
        data.loc[(raw == -1) & (raw.shift(1) != -1), "signal"] = -1
        return data
