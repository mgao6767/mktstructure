import numpy as np
import pandas as pd

from frds.measures.spread import effective_spread

from .exceptions import *

name = "EffectiveSpread"
vars_needed = {"Price", "Volume", "Mid Point", "Direction"}


def estimate(data: pd.DataFrame) -> np.ndarray:
    if not vars_needed.issubset(data.columns):
        raise MissingVariableError(name, vars_needed.difference(data.columns))

    midpt = data["Mid Point"].to_numpy()
    price = data["Price"].to_numpy()
    direction = data["Direction"].to_numpy()
    volume = data["Volume"].to_numpy()

    return effective_spread(price, midpt, volume, direction, pct_spread=True)
