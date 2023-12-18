from typing import Dict
import numpy as np
import pandas as pd

from frds.measures.lob_slope import DGGW_bid_side_slope_difference
from .exceptions import *

name = "BidSlopeDifference"
description = "Bid-side Slope Difference to examine investor patience"
vars_needed = {
    "L1-AskPrice",
    "L1-BidSize",
    "L2-BidSize",
    "L3-BidSize",
    "L4-BidSize",
    "L5-BidSize",
    "L1-BidPrice",
    "L2-BidPrice",
    "L3-BidPrice",
    "L4-BidPrice",
    "L5-BidPrice",
}


def estimate(data: pd.DataFrame) -> Dict[str, float]:
    if not vars_needed.issubset(data.columns):
        raise MissingVariableError(name, vars_needed.difference(data.columns))

    data = data.dropna(subset=vars_needed)
    level = 5

    data = data[data["L1-BidPrice"] < data["L1-AskPrice"]]

    bid_size = np.empty(shape=(len(data), level))
    bid_price = np.empty(shape=(len(data), level))
    for l in range(1, level+1):
        bid_size[:, l-1] = data[f"L{l}-BidSize"].to_numpy()
        bid_price[:, l-1] = data[f"L{l}-BidPrice"].to_numpy()

    return {name+"SimpleWeighted": DGGW_bid_side_slope_difference(bid_size, bid_price)}
