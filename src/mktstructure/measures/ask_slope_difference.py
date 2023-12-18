from typing import Dict
import numpy as np
import pandas as pd

from frds.measures.lob_slope import DGGW_ask_side_slope_difference
from .exceptions import *

name = "AskSlopeDifference"
description = "Ask-side Slope Difference to examine investor patience"
vars_needed = {
    "L1-BidPrice",
    "L1-AskSize",
    "L2-AskSize",
    "L3-AskSize",
    "L4-AskSize",
    "L5-AskSize",
    "L1-AskPrice",
    "L2-AskPrice",
    "L3-AskPrice",
    "L4-AskPrice",
    "L5-AskPrice",
}


def estimate(data: pd.DataFrame) -> Dict[str, float]:
    if not vars_needed.issubset(data.columns):
        raise MissingVariableError(name, vars_needed.difference(data.columns))

    data = data.dropna(subset=vars_needed)
    level = 5

    data = data[data["L1-BidPrice"] < data["L1-AskPrice"]]

    ask_size = np.empty(shape=(len(data), level))
    ask_price = np.empty(shape=(len(data), level))
    for l in range(1, level+1):
        ask_size[:, l-1] = data[f"L{l}-AskSize"].to_numpy()
        ask_price[:, l-1] = data[f"L{l}-AskPrice"].to_numpy()

    return {name+"SimpleWeighted": DGGW_ask_side_slope_difference(ask_size, ask_price)}
