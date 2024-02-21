"""Module for ecosystem respiration modelling"""

import datetime

import lmfit
import numpy as np
import pandas as pd

from nee_partition.timeseries import get_window_data

# Bounds for parameters
VARIABLE_BOUNDS = {
    "E0": (50, 500),  # K
    "R10": (0.0000001, 1),  # mg CO2 m-2 s-1
}

# Initial guesses for parameter values
R10_GUESS = 0.2  # mg CO2 m-2 s-1
E0_GUESS = 300  # K

# Other settings
MIN_DATA_LENGTH = 20
MIN_TEMP_RANGE = 5  # K

RELATIVE_ERROR_LIMIT = 0.5


def ecosystem_respiration(temperature: float, E0: float, R10: float) -> float:
    """Calculate soil respiration based on Lloyd & Taylor (1994)

    Args:
        temperature: Soil temperature (K)
        E0: Temperature sensitivity of respiration (K)
        R10: Ecosystem respiration at 10°C (mg CO2 m-2 s-1)

    References:
        Lloyd, J., and J. A. Taylor. 1994. ‘On the Temperature Dependence of Soil
        Respiration’. Functional Ecology 8 (3): 315–23.
        https://doi.org/10.2307/2389824.
    """
    t_ref = 283.15  # K (10°C)
    t_0 = 227.13  # K
    return R10 * np.exp(E0 * (1 / (t_ref - t_0) - 1 / (temperature - t_0)))


def fit_respiration(
    respiration: pd.Series, temperature: pd.Series, E0: float | None = None
) -> lmfit.model.ModelResult | None:
    """Fit the respiration model to data"""
    model = lmfit.Model(
        ecosystem_respiration, independent_vars=["temperature"], missing="drop"
    )
    params = model.make_params()
    params.add(
        "R10",
        value=R10_GUESS,
        min=VARIABLE_BOUNDS["R10"][0],
        max=VARIABLE_BOUNDS["R10"][1],
    )
    # If constant parameter E0 is not defined, make it a free parameter in the fit
    if E0 is None:
        params.add(
            "E0",
            value=E0_GUESS,
            min=VARIABLE_BOUNDS["E0"][0],
            max=VARIABLE_BOUNDS["E0"][1],
        )
    else:  # if value for E0 is given, make it constant in the fit
        params.add("E0", value=E0, vary=False)

    # Fit model and do checks
    mdl = model.fit(respiration.values, params, temperature=temperature.values)
    if any(  # any parameter relative error above limit
        mdl.params[par].stderr / mdl.params[par].value > RELATIVE_ERROR_LIMIT
        for par in mdl.params
    ) or any(  # any parameter value is close to boundaries
        np.isclose(mdl.params[par].value, VARIABLE_BOUNDS[par], rtol=0.01, atol=0).any()
        for par in mdl.params
    ):
        return None
    return mdl


def find_temperature_sensitivity(data: pd.DataFrame) -> tuple[float, float]:
    """Find estimate for respiration temperature response

    Args:
        data: Data frame with only night time values

    Returns:
        median, std
    """

    def fit_date(date: datetime.date) -> float:
        df = get_window_data(data, date, 7)
        # Check that there is enough data and enough variation in temperatures
        if len(df) < MIN_DATA_LENGTH | (
            df["temperature"].max() - df["temperature"].min() < MIN_TEMP_RANGE
        ):
            return np.nan
        # Fit model and extract value for E0
        mdl = fit_respiration(df["nee"], df["temperature"])
        return mdl.params["E0"].value if mdl is not None else np.nan

    model_dates = data.asfreq("D").index.date  # type: ignore
    temp_sensitivity = pd.Series(
        {d: fit_date(d) for d in model_dates}
    )
    return temp_sensitivity.median(), temp_sensitivity.std()


def create_models(
    data: pd.DataFrame, E0: float
) -> dict[datetime.date, lmfit.model.ModelResult | None]:
    """Fit models for total ecosystem response

    Uses an increasing window to select data around each date.

    Args:
        data: Data frame with only night time values of NEE and temperature
        E0: Estimate for respiration temperature sensitivity
    """

    def fit_date(date: datetime.date) -> lmfit.model.ModelResult | None:
        for window_half_width in range(2, 8):
            df = get_window_data(data, date, window_half_width)
            # If there is enough data, fit the model
            if len(df) >= MIN_DATA_LENGTH:
                return fit_respiration(df["nee"], df["temperature"], E0=E0)
        # Not enough data found within maximum window
        return None

    model_dates = data.asfreq("D").index.date  # type: ignore
    return {d: fit_date(d) for d in model_dates}
