import numpy as np
import pandas as pd

from frds.measures.lob_slope import DGGW_scaled_depth_difference
from .exceptions import *

name = "ScaledDepthDifference"
vars_needed = {
    "L1-BidSize",
    "L2-BidSize",
    "L3-BidSize",
    "L4-BidSize",
    "L5-BidSize",
    "L1-AskSize",
    "L2-AskSize",
    "L3-AskSize",
    "L4-AskSize",
    "L5-AskSize",
}


def estimate(data: pd.DataFrame, level=1) -> np.ndarray:
    if not vars_needed.issubset(data.columns):
        raise MissingVariableError(name, vars_needed.difference(data.columns))

    data = data.dropna(subset=vars_needed)

    ask_size = np.empty(shape=(len(data), level))
    bid_size = np.empty_like(ask_size)
    for l in range(1, level+1):
        ask_size[:, l-1] = data[f"L{l}-AskSize"].to_numpy()
        bid_size[:, l-1] = data[f"L{l}-BidSize"].to_numpy()

    return {name+str(level)+"SimpleWeighted": DGGW_scaled_depth_difference(bid_size, ask_size)}
