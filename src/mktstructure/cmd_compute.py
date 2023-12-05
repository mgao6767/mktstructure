import argparse
import os
from datetime import datetime as dt
from functools import partial
import pandas as pd

from . import measures
from .parx import parx
from .utils import process_files


def format_result(date, ric, measure_name, result):
    return ",".join([date, ric, measure_name, str(result)])


def afunc(func, params):
    ric, date, path = params
    df = pd.read_csv(path)
    return func(df)


def compute(measure, data):
    results = parx(partial(afunc, measure.estimate), data)
    for res, (ric, date, _) in zip(results, data):
        print(ric, date, measure.name, res)


def cmd_compute(args: argparse.Namespace):

    # Filter files to work on
    files = process_files(args.data_dir, file_pattern="*.signed.csv.gz")
    if not args.all:
        bdate = dt.fromisoformat(args.b)
        edate = dt.fromisoformat(args.e)
        files = [
            (ric, date, file_path) for ric, date, file_path in files
            if ric in args.ric and bdate <= dt.fromisoformat(date) <= edate]

    if args.bid_ask_spread:
        compute(measures.bidask_spread, files)

    # Execute
    with open(args.out, "w", encoding="utf-8") as fout:
        pass


def cmd_compute_old(args: argparse.Namespace):

    if args.out:
        fout = open(args.out, "w")

    for root, _, files in os.walk(args.data_dir):
        for f in files:
            # skip those unsigned ones
            # TODO: .csv vs .csv.gz
            if ".csv" not in f:
                continue
            if not (
                args.bid_slope
                or args.ask_slope
                or args.scaled_depth_diff_1
                or args.scaled_depth_diff_5
            ):
                if "signed" not in f:
                    continue

            path = os.path.join(root, f)
            ric, date = os.path.normpath(path).split(os.sep)[-2:]
            date = dt.fromisoformat(
                date.removesuffix(".csv")
                .removesuffix(".csv.gz")
                .removesuffix(".signed")
                .removesuffix(".sorted")
            )

            # if `--all` flag is set
            if not args.all:
                if ric not in args.ric:
                    continue

                if not (dt.fromisoformat(args.b) <= date <= dt.fromisoformat(args.e)):
                    continue

            if os.path.isfile(path):
                df = pd.read_csv(path)

                if args.bid_ask_spread:
                    _compute(measures.bidask_spread, path, date, ric, df, fout)
                if args.effective_spread:
                    _compute(measures.effective_spread,
                             path, date, ric, df, fout)
                if args.realized_spread:
                    _compute(measures.realized_spread,
                             path, date, ric, df, fout)
                if args.price_impact:
                    _compute(measures.price_impact, path, date, ric, df, fout)
                if args.variance_ratio:
                    _compute(measures.variance_ratio,
                             path, date, ric, df, fout)
                if args.bid_slope:
                    _compute(measures.bid_slope, path, date, ric, df, fout)
                if args.ask_slope:
                    _compute(measures.ask_slope, path, date, ric, df, fout)
                if args.scaled_depth_diff_1:
                    _compute(measures.sdd1, path, date, ric, df, fout)
                if args.scaled_depth_diff_5:
                    _compute(measures.sdd5, path, date, ric, df, fout)

    fout.close()


def _compute(measure, path, date, ric, data, fout):
    print(f"Computing {measure.name} for {path}")
    result = measure.estimate(data)
    # Variance ratio test returns a list of results
    if measure.name == "LoMacKinlay1988":
        assert isinstance(result, list)
        for res in result:
            for k, v in res.items():
                formated = format_result(date, ric, k, v)
                print(formated, file=fout)
    else:
        result_formated = format_result(date, ric, measure.name, result)
        print(result_formated, file=fout)
