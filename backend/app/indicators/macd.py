import pandas as pd

from app.indicators.moving_average import compute_ema


def compute_macd(
    series: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Returns (macd_line, signal_line, histogram)."""
    fast_ema = compute_ema(series, fast_period)
    slow_ema = compute_ema(series, slow_period)
    macd_line = fast_ema - slow_ema
    signal_line = compute_ema(macd_line, signal_period)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram
