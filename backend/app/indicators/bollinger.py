import pandas as pd

from app.indicators.moving_average import compute_sma


def compute_bollinger_bands(
    series: pd.Series, period: int = 20, num_std: float = 2.0
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Returns (middle_band, upper_band, lower_band)."""
    middle = compute_sma(series, period)
    std = series.rolling(window=period).std()
    upper = middle + num_std * std
    lower = middle - num_std * std
    return middle, upper, lower
