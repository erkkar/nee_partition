"""Module for ecosystem respiration modelling"""

import datetime

import lmfit
import numpy as np
import pandas as pd

from nee_partition.timeseries import get_window_data

# Bounds for parameters
VARIABLE_BOUNDS = {
    "E": (50, 500),  # K-1
    "R0": (0.0000001, 1),  # mg CO2 m-2 s-1
}

# Initial guesses for parameter values
R0_GUESS = 0.2  # mg CO2 m-2 s-1
E_GUESS = 300  # K-1

# Other settings
MIN_DATA_LENGTH = 20
MIN_TEMP_RANGE = 5  # K

RELATIVE_ERROR_LIMIT = 0.5


def ecosystem_respiration(temperature: float, E: float, R0: float) -> float:
    """Calculate soil respiration based on Lloyd & Taylor (1994)

    Args:
        temperature: Soil temperature (K)
        E: Temperature sensitivity of respiration (K-1)
        R0: Ecosystem respiration at 10°C (mg CO2 m-2 s-1)

    References:
        Lloyd, J., and J. A. Taylor. 1994. ‘On the Temperature Dependence of Soil
        Respiration’. Functional Ecology 8 (3): 315–23.
        https://doi.org/10.2307/2389824.
    """
    temp0 = 56.02  # K
    temp1 = 227.13  # K
    return R0 * np.exp(E * ((1 / temp0) - (1 / (temperature - temp1))))


def fit_respiration(
    respiration: pd.Series, temperature: pd.Series, E: float | None = None
) -> lmfit.model.ModelResult | None:
    """Fit the respiration model to data"""
    model = lmfit.Model(
        ecosystem_respiration, independent_vars=["temperature"], missing="drop"
    )
    params = model.make_params()
    params.add(
        "R0",
        value=R0_GUESS,
        min=VARIABLE_BOUNDS["R0"][0],
        max=VARIABLE_BOUNDS["R0"][1],
    )
    # If constant parameter E is not defined, make it a free parameter in the fit
    if E is None:
        params.add(
            "E",
            value=E_GUESS,
            min=VARIABLE_BOUNDS["E"][0],
            max=VARIABLE_BOUNDS["E"][1],
        )
    else:  # if value for E is given, make it constant in the fit
        params.add("E", value=E, vary=False)

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


def find_temperature_response(data: pd.DataFrame) -> tuple[float, float]:
    """Find estimate for respiration temperature response

    Args:
        data: Data frame with only night time values

    Returns:
        median, std
    """

    def fit_temperature_response_date(date: datetime.date) -> float:
        df = get_window_data(data, date, 7)
        # Check that there is enough data and enough variation in temperatures
        if len(df) < MIN_DATA_LENGTH | (
            df["temperature"].max() - df["temperature"].min() < MIN_TEMP_RANGE
        ):
            return np.nan
        # Fit model and extract value for E
        mdl = fit_respiration(df["nee"], df["temperature"])
        return mdl.params["E"].value if mdl is not None else np.nan

    model_dates = data.asfreq("D").index.date  # type: ignore
    temp_response = pd.Series(
        {d: fit_temperature_response_date(d) for d in model_dates}
    )
    return temp_response.median(), temp_response.std()


def create_models(
    data: pd.DataFrame, E: float
) -> dict[datetime.date, lmfit.model.ModelResult | None]:
    """Fit models for total ecosystem response

    Uses an increasing window to select data around each date.

    Args:
        data: Data frame with only night time values of NEE and temperature
        E: Estimate for respiration temperature sensitivity
    """

    def fit_date(date: datetime.date) -> lmfit.model.ModelResult | None:
        for window_half_width in range(2, 8):
            df = get_window_data(data, date, window_half_width)
            # If there is enough data, fit the model
            if len(df) >= MIN_DATA_LENGTH:
                return fit_respiration(df["nee"], df["temperature"], E=E)
        # Not enough data found within maximum window
        return None

    model_dates = data.asfreq("D").index.date  # type: ignore
    return {d: fit_date(d) for d in model_dates}
