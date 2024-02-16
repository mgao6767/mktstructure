from typing import Dict
import numpy as np
import pandas as pd

from frds.measures import PIN
from .exceptions import *

name = "PIN"
vars_needed = {"Direction"}


def estimate(data: pd.DataFrame, interval_mins=15) -> Dict[str, float]:
    if not vars_needed.issubset(data.columns):
        raise MissingVariableError(name, vars_needed.difference(data.columns))

    # Resample to 15-minute intervals and sum the buys and sells
    data = data.resample(f'{int(interval_mins)}min')

    if len(data["Direction"]) < 2:
        return {f"{name}_EHO2010_{interval_mins}min": np.nan, f"{name}_LK2011_{interval_mins}min": np.nan}

    # Define a function to count the occurrences of 1 and -1
    def count_occurrences(data):
        counts = data.value_counts()
        buys = counts.get(1, 0)  # Count of 1s (buys)
        sells = counts.get(-1, 0)  # Count of -1s (sells)
        return pd.Series([buys, sells], index=['buys', 'sells'])

    # Apply the function to each resampled interval
    frequency_data = data['Direction'].apply(count_occurrences)

    # Extract the frequencies for buys and sells
    buys = frequency_data['buys'].values
    sells = frequency_data['sells'].values

    assert buys.shape == sells.shape

    pin_eho2010 = PIN(buys, sells).estimate(method="EHO2010").pin
    pin_lk2011 = PIN(buys, sells).estimate(method="LK2011").pin

    return {f"{name}_EHO2010_{interval_mins}min": pin_eho2010, f"{name}_LK2011_{interval_mins}min": pin_lk2011}


if __name__ == "__main__":

    from mktstructure.utils import transform_taq

    df = pd.read_csv(
        r"F:\MKTSTRUCTURE\data\A.N\2012-01-03.sorted.signed.csv.gz")
    df = transform_taq(df)

    res = estimate(df)
    print(res)
