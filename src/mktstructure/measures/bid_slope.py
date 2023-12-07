from typing import Dict
import numpy as np
import pandas as pd

from frds.measures.lob_slope import DGGW_bid_slope
from .exceptions import *

name = "BidSlope"
vars_needed = {
    "L1-BidPrice",
    "L1-AskPrice",
    "L1-BidSize",
    "L2-BidSize",
    "L3-BidSize",
    "L4-BidSize",
    "L5-BidPrice",
    "L5-BidSize",
}


def estimate(data: pd.DataFrame) -> Dict[str, float]:
    if not vars_needed.issubset(data.columns):
        raise MissingVariableError(name, vars_needed.difference(data.columns))

    data = data.dropna(subset=vars_needed)
    level = 5

    data = data[data["L1-BidPrice"] < data["L1-AskPrice"]]

    bid_size = np.empty(shape=(len(data), level))
    for l in range(1, level+1):
        bid_size[:, l-1] = data[f"L{l}-BidSize"].to_numpy()

    bid_price_highest_level = data[f"L{level}-BidPrice"].to_numpy()
    midpt = (data["L1-BidPrice"] + data["L1-AskPrice"]).to_numpy() / 2

    return {name+str(level)+"SimpleWeighted": DGGW_bid_slope(bid_size, bid_price_highest_level, midpt)}
