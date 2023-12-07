from typing import Dict
import numpy as np
import pandas as pd

from frds.measures.lob_slope import DGGW_ask_slope
from .exceptions import *

name = "AskSlope"
description = "Ask Slope to examine the liquidity available to investors wishing to execute a buy market order"
vars_needed = {
    "L1-BidPrice",
    "L1-AskPrice",
    "L1-AskSize",
    "L2-AskSize",
    "L3-AskSize",
    "L4-AskSize",
    "L5-AskPrice",
    "L5-AskSize",
}


def estimate(data: pd.DataFrame) -> Dict[str, float]:
    if not vars_needed.issubset(data.columns):
        raise MissingVariableError(name, vars_needed.difference(data.columns))

    data = data.dropna(subset=vars_needed)
    level = 5

    data = data[data["L1-BidPrice"] < data["L1-AskPrice"]]

    ask_size = np.empty(shape=(len(data), level))
    for l in range(1, level+1):
        ask_size[:, l-1] = data[f"L{l}-AskSize"].to_numpy()

    ask_price_highest_level = data[f"L{level}-AskPrice"].to_numpy()
    midpt = (data["L1-BidPrice"] + data["L1-AskPrice"]).to_numpy() / 2

    # This measure may not be comparable across stocks given that it's
    # total depth / (price - midpoint)
    return {name+str(level)+"SimpleWeighted": DGGW_ask_slope(ask_size, ask_price_highest_level, midpt)}
