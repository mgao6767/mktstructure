import argparse
from typing import Callable
from datetime import datetime as dt
from functools import partial
import pandas as pd

from . import measures
from .parx import parx
from .utils import process_files, transform_taq


def format_result(date, ric, measure_name, result):
    return ",".join([date, ric, measure_name, str(result)])


def afunc(func, params):
    ric, date, path = params
    df = pd.read_csv(path)
    df = transform_taq(df)
    return func(df)


def _compute(measure, data, out_filepath="results.csv"):
    assert hasattr(measure, "estimate")
    assert isinstance(measure.estimate, Callable)
    results = parx(partial(afunc, measure.estimate), data)

    with open(out_filepath, "w", encoding="utf-8") as fout:
        for res, (ric, date, _) in zip(results, data):
            assert isinstance(res, dict)
            for name, value in res.items():
                print(format_result(date, ric, name, value), file=fout)
            # # Variance ratio test returns a list of results
            # if measure.name == "LoMacKinlay1988":
            #     assert isinstance(res, list)
            #     for r in res:
            #         for k, v in r.items():
            #             formated = format_result(date, ric, k, v)
            #             print(formated, file=fout)
            # else:
            #     result_formated = format_result(date, ric, measure.name, res)
            #     print(result_formated, file=fout)


def get_trades_and_quotes(args: argparse.Namespace):
    """
    Retrieves and processes trade and quote files based on specified arguments.

    This function processes files located in a specified data directory. It 
    filters and returns signed trades and quotes based on a given set of 
    criteria. The criteria include the type of files to process, a date range, 
    and specific RICs (Reuters Instrument Codes).

    Here, we assume that the TAQ data has been sorted.
    "*.signed-trades.csv.gz" contains signed trades and corresponding quotes.
    "*.quotes.csv.gz" contains quotes only.
    (In different data directory)
    "????-??-??.csv.gz" contains LOB bid ask data.

    Parameters:
    args (argparse.Namespace): A namespace object from argparse containing 
        the following attributes:
        - data_dir (str): Directory where the data files are located.
        - ric (list of str): List of RICs to filter the data.
        - b (str): Beginning date in ISO format (inclusive) for filtering data.
        - e (str): Ending date in ISO format (inclusive) for filtering data.
        - all (bool): Flag to indicate whether to process all data without 
            date and RIC filtering.

    Returns:
    tuple: A tuple containing two lists:
        - signed_trades (list): A list of tuples (ric, date, file_path) for 
            signed trades that meet the filtering criteria.
        - quotes (list): A list of tuples (ric, date, file_path) for quotes 
            that meet the filtering criteria.
    """
    signed_trades = process_files(
        args.data_dir, file_pattern="*.signed-trades.csv.gz")
    quotes = process_files(
        args.data_dir, file_pattern="*.quotes.csv.gz")
    lob_data = process_files(
        args.data_dir, file_pattern="????-??-??.csv.gz")

    if not args.all:
        bdate = dt.fromisoformat(args.b)
        edate = dt.fromisoformat(args.e)
        signed_trades = [
            (ric, date, file_path) for ric, date, file_path in signed_trades
            if ric in args.ric and bdate <= dt.fromisoformat(date) <= edate]
        quotes = [
            (ric, date, file_path) for ric, date, file_path in quotes
            if ric in args.ric and bdate <= dt.fromisoformat(date) <= edate]
        lob_data = [
            (ric, date, file_path) for ric, date, file_path in lob_data
            if ric in args.ric and bdate <= dt.fromisoformat(date) <= edate]

    return signed_trades, quotes, lob_data


def cmd_compute(args: argparse.Namespace):

    signed_trades, quotes, lob_data = get_trades_and_quotes(args)
    compute = partial(_compute, out_filepath=args.out)

    # quoted-spread based on quotes not trades
    if args.quoted_spread:
        compute(measures.quoted_spread, quotes)

    # others use signed trades (and quotes)
    if args.effective_spread:
        compute(measures.effective_spread, signed_trades)
    if args.realized_spread:
        compute(measures.realized_spread, signed_trades)
    if args.price_impact:
        compute(measures.price_impact, signed_trades)
    if args.variance_ratio:
        compute(measures.variance_ratio, signed_trades)
    if args.kyle_lambda:
        compute(measures.kyle_lambda, signed_trades)

    # These use LOB data
    if args.bid_slope:
        compute(measures.bid_slope, lob_data)
    if args.ask_slope:
        compute(measures.ask_slope, lob_data)
    if args.scaled_depth_diff_1:
        compute(measures.sdd1, lob_data)
    if args.scaled_depth_diff_5:
        compute(measures.sdd5, lob_data)
