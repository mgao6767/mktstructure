from . import (
    quoted_spread,
    effective_spread,
    realized_spread,
    price_impact,
    variance_ratio,
    bid_slope,
    ask_slope,
    scaled_depth_difference,
    kyle_lambda,
    bid_slope_difference,
    ask_slope_difference,
    pin,
    vwap
)


class sdd1:
    name = "ScaledDepthDifferenceLvl1"

    @staticmethod
    def estimate(df):
        return scaled_depth_difference.estimate(df, 1)


class sdd5:
    name = "ScaledDepthDifferenceLvl5"

    @staticmethod
    def estimate(df):
        return scaled_depth_difference.estimate(df, 5)


class pin30min:
    name = "PIN_30min"

    @staticmethod
    def estimate(df):
        return pin.estimate(df, 30)
