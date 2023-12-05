import numpy as np
import pandas as pd

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


def estimate(data: pd.DataFrame) -> np.ndarray:
    if not vars_needed.issubset(data.columns):
        raise MissingVariableError(name, vars_needed.difference(data.columns))

    data = data.dropna(subset=vars_needed)

    slope = np.divide(
        data["L1-AskSize"].to_numpy()
        + data["L2-AskSize"].to_numpy()
        + data["L3-AskSize"].to_numpy()
        + data["L4-AskSize"].to_numpy()
        + data["L5-AskSize"].to_numpy(),
        data["L5-AskPrice"] - (data["L1-AskPrice"] - data["L1-BidPrice"]) / 2,
    )
    return np.mean(slope) if len(slope) else np.nan
