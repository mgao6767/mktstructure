from typing import Dict
import numpy as np
import pandas as pd

from frds.measures.spread import quoted_spread
from .exceptions import *

name = "QuotedSpread"
description = "Simple average quoted bid-ask spread"
vars_needed = {"Bid Price", "Ask Price"}


def estimate(data: pd.DataFrame) -> Dict[str, float]:
    if not vars_needed.issubset(data.columns):
        raise MissingVariableError(name, vars_needed.difference(data.columns))

    ask = data["Ask Price"].to_numpy()
    bid = data["Bid Price"].to_numpy()

    # Calculate the bid-ask spread (pct)
    data['Spread'] = 2*(ask - bid) / (ask + bid) * 100

    # Calculate time intervals in seconds (or any other unit of time)
    data['Time Interval'] = data.index.to_series(
    ).diff().dt.total_seconds().shift(-1)

    # Handle the last interval (optional)
    data.iloc[-1, data.columns.get_loc('Time Interval')] = np.nan

    # Compute the time-weighted bid-ask spread
    time_weighted_spread = (data['Spread'] * data['Time Interval']
                            ).sum() / data['Time Interval'].sum()

    return {name+"SimpleWeighted": quoted_spread(bid, ask, pct_spread=True),
            name+"TimeWeighted": time_weighted_spread}
