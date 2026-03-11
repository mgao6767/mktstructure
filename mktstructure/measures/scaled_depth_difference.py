import numpy as np
import pandas as pd

from .exceptions import *

name = "ScaledDepthDifference"
description = "Scaled Depth Difference to examine the relative level of asymmetry in the order book at a particular point in time"
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

    # Cumulative depth up to the given level
    bid_cols = [f"L{i}-BidSize" for i in range(1, level + 1)]
    ask_cols = [f"L{i}-AskSize" for i in range(1, level + 1)]

    # Only drop rows where the columns we actually use have NaN
    used_cols = bid_cols + ask_cols
    data = data.dropna(subset=used_cols)

    cum_bid = data[bid_cols].sum(axis=1).to_numpy()
    cum_ask = data[ask_cols].sum(axis=1).to_numpy()

    denom = cum_ask + cum_bid

    slope = np.divide(
        2 * (cum_ask - cum_bid),
        denom,
        out=np.full_like(denom, np.nan, dtype=float),
        where=denom != 0,
    )

    return np.nanmean(slope) if len(slope) else np.nan
