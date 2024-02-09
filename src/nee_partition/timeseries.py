"""Module for time series related helper functions"""

import datetime

import pandas as pd


def get_window_data(
    data: pd.DataFrame, date: datetime.date, window_half_width_days: int
) -> pd.DataFrame:
    """Extract data for the given date and window width"""
    # Precalculate dates of the index
    dates = data.index.date  # type: ignore
    return data.loc[
        (dates >= date - datetime.timedelta(days=window_half_width_days))
        & (dates <= date + datetime.timedelta(days=window_half_width_days))
    ]
