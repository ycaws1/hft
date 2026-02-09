from abc import ABC, abstractmethod

import pandas as pd

from app.models.domain import StrategyParamDef


class Strategy(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Machine-readable identifier."""

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Brief description of the strategy."""

    @property
    @abstractmethod
    def category(self) -> str:
        """'technical' or 'quant'."""

    @abstractmethod
    def parameters(self) -> list[StrategyParamDef]:
        """Declare configurable parameters."""

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame, params: dict) -> pd.DataFrame:
        """Add 'signal' column (1=buy, -1=sell, 0=hold) and indicator columns."""

    def validate_params(self, params: dict) -> dict:
        declared = {p.name: p for p in self.parameters()}
        validated = {}
        for pname, pdef in declared.items():
            val = params.get(pname, pdef.default)
            if pdef.type == "int":
                val = int(val)
                if pdef.min is not None:
                    val = max(val, int(pdef.min))
                if pdef.max is not None:
                    val = min(val, int(pdef.max))
            elif pdef.type == "float":
                val = float(val)
                if pdef.min is not None:
                    val = max(val, pdef.min)
                if pdef.max is not None:
                    val = min(val, pdef.max)
            elif pdef.type == "select" and pdef.options:
                if val not in pdef.options:
                    val = pdef.default
            validated[pname] = val
        return validated
