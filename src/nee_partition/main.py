"""Main module"""

import pandas as pd
from pyprojroot import here

from nee_partition import respiration

VARIABLES = {"temperature": "TA", "ppfd": "PAR", "nee": "NEE"}
PPFD_THRESHOLD = 20  # µmol m-2 s-1

alldata = pd.read_csv(
    here() / "Kalevansuo.csv", index_col="TIMESTAMP_END", parse_dates=True
).rename(columns={data_var: variable for variable, data_var in VARIABLES.items()})


def main():
    """Partition NEE into GPP and TER"""

    night_data = alldata.where(alldata["ppfd"] < PPFD_THRESHOLD)[
        ["temperature", "nee"]
    ].dropna()
    temp_sensitivity, temp_sensitivity_err = respiration.find_temperature_sensitivity(
        night_data
    )

    resp_models = respiration.create_models(night_data, temp_sensitivity)

    return resp_models
