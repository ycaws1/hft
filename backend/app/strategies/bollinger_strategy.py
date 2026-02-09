import pandas as pd

from app.indicators.bollinger import compute_bollinger_bands
from app.models.domain import StrategyParamDef
from app.strategies.base import Strategy


class BollingerStrategy(Strategy):
    @property
    def name(self) -> str:
        return "bollinger"

    @property
    def display_name(self) -> str:
        return "Bollinger Bands"

    @property
    def description(self) -> str:
        return "Buy when price touches lower band, sell when it touches upper band."

    @property
    def category(self) -> str:
        return "technical"

    def parameters(self) -> list[StrategyParamDef]:
        return [
            StrategyParamDef(name="period", label="BB Period", type="int", default=20, min=5, max=100),
            StrategyParamDef(name="num_std", label="Std Deviations", type="float", default=2.0, min=0.5, max=4.0),
        ]

    def generate_signals(self, data: pd.DataFrame, params: dict) -> pd.DataFrame:
        params = self.validate_params(params)
        middle, upper, lower = compute_bollinger_bands(
            data["close"], params["period"], params["num_std"]
        )
        data["bb_middle"] = middle
        data["bb_upper"] = upper
        data["bb_lower"] = lower

        # Raw position: 1 when below lower band, -1 when above upper band
        raw = pd.Series(0, index=data.index)
        raw[data["close"] <= lower] = 1
        raw[data["close"] >= upper] = -1

        # Only signal on transitions (crossover)
        data["signal"] = 0
        data.loc[(raw == 1) & (raw.shift(1) != 1), "signal"] = 1
        data.loc[(raw == -1) & (raw.shift(1) != -1), "signal"] = -1
        return data
