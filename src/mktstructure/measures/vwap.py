from typing import Dict
import pandas as pd

from .exceptions import *

name = "VWAP"
vars_needed = {"Price", "Volume", "Direction"}


def estimate(data: pd.DataFrame) -> Dict[str, float]:
    if not vars_needed.issubset(data.columns):
        raise MissingVariableError(name, vars_needed.difference(data.columns))

    price = data["Price"].to_numpy()
    volume = data["Volume"].to_numpy()

    vwap = (price*volume).sum() / volume.sum()

    _buys = data[data['Direction'] == 1]
    price_buys = _buys["Price"].to_numpy()
    volume_buys = _buys["Volume"].to_numpy()

    _sells = data[data['Direction'] == -1]
    price_sells = _sells["Price"].to_numpy()
    volume_sells = _sells["Volume"].to_numpy()

    vwap_buys = (price_buys*volume_buys).sum() / volume_buys.sum()
    vwap_sells = (price_sells*volume_sells).sum() / volume_sells.sum()

    return {"VWAP": vwap,
            "VWAPBuys": vwap_buys,
            "VWAPSells": vwap_sells}
