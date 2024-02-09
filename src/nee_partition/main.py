"""Main module"""

import pandas as pd
from pyprojroot import here

from nee_partition import respiration

VARIABLES = {"temperature": "TA", "ppfd": "PAR", "nee": "NEE"}

alldata = pd.read_csv(
    here() / "Kalevansuo.csv", index_col="TIMESTAMP_END", parse_dates=True
).rename(columns={data_var: variable for variable, data_var in VARIABLES.items()})


def main():
    """Partition NEE into GPP and TER"""

    night_data = alldata.where(alldata["ppfd"] < 20)[["temperature", "nee"]].dropna()
    temp_response, temp_response_err = respiration.find_temperature_response(night_data)

    resp_models = respiration.create_models(night_data, temp_response)

    return resp_models
