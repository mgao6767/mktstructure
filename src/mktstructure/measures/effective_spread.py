from typing import Dict
import pandas as pd

from frds.measures.spread import effective_spread

from .exceptions import *

name = "EffectiveSpread"
vars_needed = {"Price", "Volume", "Mid Point", "Direction"}


def estimate(data: pd.DataFrame) -> Dict[str, float]:
    if not vars_needed.issubset(data.columns):
        raise MissingVariableError(name, vars_needed.difference(data.columns))

    midpt = data["Mid Point"].to_numpy()
    price = data["Price"].to_numpy()
    direction = data["Direction"].to_numpy()
    volume = data["Volume"].to_numpy()

    return {name+"WithDirection": effective_spread(price, midpt, volume, direction, pct_spread=True),
            name+"AbsoluteVal": effective_spread(price, midpt, volume, trade_direction=None, pct_spread=True)}
