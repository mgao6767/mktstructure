import numpy as np
import pandas as pd

from .exceptions import *

name = "BidSlope"
description = "Bid Slope to examine the liquidity available to investors wishing to execute a sell market order"
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


def estimate(data: pd.DataFrame) -> np.ndarray:
    if not vars_needed.issubset(data.columns):
        raise MissingVariableError(name, vars_needed.difference(data.columns))

    data = data.dropna(subset=vars_needed)

    slope = -np.divide(
        data["L1-BidSize"].to_numpy()
        + data["L2-BidSize"].to_numpy()
        + data["L3-BidSize"].to_numpy()
        + data["L4-BidSize"].to_numpy()
        + data["L5-BidSize"].to_numpy(),
        data["L5-BidPrice"] - (data["L1-AskPrice"] - data["L1-BidPrice"]) / 2,
    )
    return np.mean(slope) if len(slope) else np.nan
