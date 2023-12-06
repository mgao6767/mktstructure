import pandas as pd
import numpy as np
from numba import jit


def lee_and_ready(df: pd.DataFrame) -> pd.DataFrame:
    # Prepare for Lee and Ready.
    prices = df["Price"].to_numpy()
    bids = df["Bid Price"].to_numpy()
    asks = df["Ask Price"].to_numpy()
    bidsize = df["Bid Size"].to_numpy()
    asksize = df["Ask Size"].to_numpy()
    directions, bbids, basks = _lee_and_ready_classify(
        prices, bids, asks, bidsize, asksize
    )
    df["Direction"] = pd.Series(directions, index=df.index)
    df["Bid Price"] = pd.Series(bbids, index=df.index)
    df["Ask Price"] = pd.Series(basks, index=df.index)
    df["Mid Point"] = (df["Bid Price"] + df["Ask Price"]) / 2
    # If the first observation is a Trade, there will not be a Mid Point.
    return df[df["Type"] == "Trade"].dropna(subset=["Mid Point"])


@jit(nopython=True, nogil=True, cache=True)
def _lee_and_ready_classify(prices, bids, asks, bidsize, asksize):
    n = len(prices)
    directions = np.zeros(n, dtype=np.int8)
    last_bid, last_ask = np.nan, np.nan
    last_trade_price, last2_trade_price = np.nan, np.nan
    last_quote_midpoint = np.nan
    for i in range(n):
        # If price[i] is np.nan then this is a quote.
        if np.isnan(prices[i]) and asks[i] and bids[i] and bidsize[i] and asksize[i]:
            last_quote_midpoint = (last_bid + last_ask) / 2
            last_bid, last_ask = bids[i], asks[i]
            continue
        # Up here we know this is a trade.
        p = prices[i]
        # Quote Test
        if np.isnan(last_quote_midpoint):
            pass
        elif p > last_quote_midpoint:
            directions[i] = 1
        elif p < last_quote_midpoint:
            directions[i] = -1
        # Ticke Test when price = last midpoint
        elif np.isnan(last_trade_price):
            pass
        elif p > last_trade_price:
            directions[i] = 1
        elif p < last_trade_price:
            directions[i] = -1
        elif np.isnan(last2_trade_price):
            pass
        elif p > last2_trade_price:
            directions[i] = 1
        elif p < last2_trade_price:
            directions[i] = -1
        # The immediate bid/ask before the trade.
        if not np.isnan(last_bid):
            bids[i] = last_bid
        if not np.isnan(last_ask):
            asks[i] = last_ask
        last2_trade_price = last_trade_price
        last_trade_price = p
    return directions, bids, asks
