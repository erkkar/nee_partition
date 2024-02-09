"""Module for partitioning NEE"""

import datetime

import lmfit
import numpy as np
import pandas as pd
from pyprojroot import here

from nee_partition.models import ecosystem_respiration

VARIABLES = {"temperature": "TA", "ppfd": "PAR", "nee": "NEE"}

alldata = pd.read_csv(
    here() / "Kalevansuo.csv", index_col="TIMESTAMP_END", parse_dates=True
).rename(columns={data_var: variable for variable, data_var in VARIABLES.items()})

# Bounds for parameters
VARIABLE_BOUNDS = {
    "E": (50, 500),  # K-1
    "R0": (0.0000001, 1),  # mg CO2 m-2 s-1
    "alpha": (-0.02, -0.0000001),  # µmol-1 m2 s1
    "gp_max": (-5, -0.00000001),  # mg CO2 m-2 s-1
}

R0_GUESS = 0.2
E_GUESS = 300  # mg CO2 m-2 s-1 K-1


def fit_respiration(
    respiration: pd.Series, temperature: pd.Series, E: float | None = None
) -> lmfit.model.ModelResult:
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
    else:  # If value for E is given, make it constant in the fit
        params.add("E", value=E, vary=False)

    return model.fit(respiration.values, params, temperature=temperature.values)


WINDOW_HALF_WIDTH_DAYS = 7
MIN_DATA_LENGTH = 20
MIN_TEMP_RANGE = 5  # K


def find_temperature_response(data: pd.DataFrame) -> tuple[float, float]:
    """Find estimate for respiration temperature response

    Args:
        data: Data frame with only night time values

    Returns:
        median, std
    """

    dates = data.index.date  # type: ignore
    model_dates = data.asfreq("D").index.date  # type: ignore

    def fit_temperature_response_date(date: datetime.date) -> float:
        df = data.loc[
            (dates >= date - datetime.timedelta(days=WINDOW_HALF_WIDTH_DAYS))
            & (dates <= date + datetime.timedelta(days=WINDOW_HALF_WIDTH_DAYS))
        ]
        # Check that there is enough data with enough temp. variation
        if len(df) < MIN_DATA_LENGTH | (
            df["temperature"].max() - df["temperature"].min() < MIN_TEMP_RANGE
        ):
            return np.nan
        return fit_respiration(df["nee"], df["temperature"]).params["E"].value

    temp_response = pd.Series(
        {d: fit_temperature_response_date(d) for d in model_dates}
    )
    return temp_response.median(), temp_response.std()


def main():
    """Partition NEE into GPP and TER"""

    night_data = alldata.where(alldata["ppfd"] < 20)
    temp_response, temp_response_err = find_temperature_response(night_data)
    return temp_response
