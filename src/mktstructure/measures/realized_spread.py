import numpy as np
import pandas as pd

from frds.measures.spread import realized_spread
from .exceptions import *

name = "RealizedSpread"
vars_needed = {"Price", "Volume", "Mid Point", "Direction"}


def estimate(data: pd.DataFrame) -> np.ndarray:
    midpt = data["Mid Point"].to_numpy()
    price = data["Price"].to_numpy()
    timestamps = np.array(data.index, dtype="datetime64")
    # Find the Quote Mid Point 5 min later than each trade.
    matched_midpt = []
    for idx, ts1 in enumerate(timestamps):
        for i, ts2 in enumerate(timestamps[idx:]):
            if ts2 - ts1 >= np.timedelta64(5, "m"):
                matched_midpt.append(midpt[idx + i])
                break

    matched = len(matched_midpt)
    direction = data["Direction"].to_numpy()[:matched]
    volume = data["Volume"].to_numpy()[:matched]
    midpt = midpt[:matched]
    price = price[:matched]

    return realized_spread(price, matched_midpt, midpt, volume, direction, pct_spread=True)
