import numpy as np
import pandas as pd

from .exceptions import *

name = "ScaledDepthDifference"
description = "Scaled Depth Difference to examine the relative level of asymmetry in the order book at a particular point in time"
vars_needed = {
    "L1-BidPrice",
    "L2-BidPrice",
    "L3-BidPrice",
    "L4-BidPrice",
    "L5-BidPrice",
    "L1-AskPrice",
    "L2-AskPrice",
    "L3-AskPrice",
    "L4-AskPrice",
    "L5-AskPrice",
}


def estimate(data: pd.DataFrame, level=1) -> np.ndarray:
    if not vars_needed.issubset(data.columns):
        raise MissingVariableError(name, vars_needed.difference(data.columns))

    data = data.dropna(subset=vars_needed)

    slope = np.divide(
        data[f"L{level}-AskSize"].to_numpy() - data[f"L{level}-BidSize"].to_numpy(),
        data[f"L{level}-AskSize"].to_numpy() + data[f"L{level}-BidSize"].to_numpy(),
    )

    return np.mean(slope) if len(slope) else np.nan
