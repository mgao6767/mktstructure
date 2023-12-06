import numpy as np
import pandas as pd

from frds.measures.price_impact import simple_price_impact
from .exceptions import *

name = "PriceImpact"
vars_needed = {"Price", "Volume", "Mid Point", "Direction"}


def estimate(data: pd.DataFrame) -> np.ndarray:
    if not vars_needed.issubset(data.columns):
        raise MissingVariableError(name, vars_needed.difference(data.columns))

    midpt = data["Mid Point"].to_numpy()
    price = data["Price"].to_numpy()
    # timestamps needs to be sorted!
    timestamps = np.array(data.index, dtype="datetime64")
    # Find the Quote Mid Point 5 min later than each trade.
    # This actually finds the next trade 5min later and the quote mid point
    # Add 5 minutes to each timestamp
    timestamps_p5min = timestamps + np.timedelta64(5, 'm')
    nearest_positions = np.searchsorted(
        timestamps, timestamps_p5min, side='left')
    valid_positions = nearest_positions[nearest_positions < len(timestamps)]
    matched_midpt = midpt[valid_positions]

    matched = len(matched_midpt)
    direction = data["Direction"].to_numpy()[:matched]
    volume = data["Volume"].to_numpy()[:matched]
    midpt = midpt[:matched]
    price = price[:matched]

    return {name+"withDirection": simple_price_impact(price, matched_midpt, midpt, volume, direction, pct_spread=True),
            name+"AbsoluteVal": simple_price_impact(price, matched_midpt, midpt, volume, trade_direction=None, pct_spread=True)}
