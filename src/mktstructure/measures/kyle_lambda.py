from typing import Dict
import numpy as np
import pandas as pd

from frds.measures import kyle_lambda
from .exceptions import *

name = "KyelLambda"
vars_needed = {"Price", "Volume", "Direction"}


def estimate(data: pd.DataFrame) -> Dict[str, float]:
    if not vars_needed.issubset(data.columns):
        raise MissingVariableError(name, vars_needed.difference(data.columns))

    # Compute signed square root dollar volume
    data['DollarVolume'] = data['Price'] * data['Volume']
    data['SignedSqrtDollarVolume'] = data['Direction'] * \
        np.sqrt(np.abs(data['DollarVolume']))

    # Resample to 5-minute intervals and sum the values
    data = data.resample('5min')
    if len(data["Price"]) < 2:
        return {name: np.nan}

    # `pct_change()` calculates fractional change
    # (also known as per unit change or relative change) and not percentage change
    returns = data['Price'].last().pct_change().dropna().to_numpy() * 100
    signed_dollar_volume = data['SignedSqrtDollarVolume'].sum(
    ).to_numpy().flatten()[1:]

    # print(returns.shape, signed_dollar_volume.shape)
    assert returns.shape == signed_dollar_volume.shape

    return {name: kyle_lambda(returns, signed_dollar_volume)}
