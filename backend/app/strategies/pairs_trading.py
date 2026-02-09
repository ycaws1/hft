import pandas as pd

from app.models.domain import StrategyParamDef
from app.strategies.base import Strategy


class PairsTradingStrategy(Strategy):
    @property
    def name(self) -> str:
        return "pairs_trading"

    @property
    def display_name(self) -> str:
        return "Pairs Trading"

    @property
    def description(self) -> str:
        return "Trade the spread between two correlated stocks using z-score. Requires exactly 2 symbols."

    @property
    def category(self) -> str:
        return "quant"

    def parameters(self) -> list[StrategyParamDef]:
        return [
            StrategyParamDef(name="lookback", label="Lookback Period", type="int", default=30, min=10, max=200),
            StrategyParamDef(name="entry_z", label="Entry Z-Score", type="float", default=2.0, min=0.5, max=4.0),
            StrategyParamDef(name="exit_z", label="Exit Z-Score", type="float", default=0.5, min=0.0, max=2.0),
        ]

    def generate_signals(self, data: pd.DataFrame, params: dict) -> pd.DataFrame:
        """For pairs trading, data must have 'close' and 'close_2' columns.
        Signals apply to the first symbol: 1 = buy stock1/sell stock2, -1 = reverse."""
        params = self.validate_params(params)

        if "close_2" not in data.columns:
            data["signal"] = 0
            return data

        spread = data["close"] - data["close_2"]
        rolling_mean = spread.rolling(window=params["lookback"]).mean()
        rolling_std = spread.rolling(window=params["lookback"]).std()
        data["spread"] = spread
        data["spread_z"] = (spread - rolling_mean) / rolling_std

        data["signal"] = 0
        # Buy stock1 (sell stock2) when spread z-score drops below -entry_z
        data.loc[data["spread_z"] <= -params["entry_z"], "signal"] = 1
        # Sell stock1 (buy stock2) when spread z-score rises above entry_z
        data.loc[data["spread_z"] >= params["entry_z"], "signal"] = -1
        # Close position when z-score returns near zero
        data.loc[data["spread_z"].abs() <= params["exit_z"], "signal"] = 0
        return data
