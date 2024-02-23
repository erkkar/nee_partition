"""Main module"""

from pathlib import Path

import pandas as pd

from nee_partition import respiration

VARIABLES = {"temperature": "TA", "ppfd": "PAR", "nee": "NEE"}
INDEX_COL = "TIMESTAMP_END"
PPFD_THRESHOLD = 20  # µmol m-2 s-1


def main(data_file_path: Path | str):
    """Partition NEE into GPP and TER"""

    # Read in data
    data = pd.read_csv(data_file_path, index_col=INDEX_COL, parse_dates=True).rename(
        columns={data_var: variable for variable, data_var in VARIABLES.items()}
    )

    night_data = data.where(data["ppfd"] < PPFD_THRESHOLD)[
        ["temperature", "nee"]
    ].dropna()
    temp_sensitivity, temp_sensitivity_err = respiration.find_temperature_sensitivity(
        night_data
    )

    resp_models = respiration.create_models(night_data, temp_sensitivity)

    return resp_models
