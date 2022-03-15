import argparse
import os
from datetime import datetime as dt

import pandas as pd

from . import measures


def format_result(date, ric, measure_name, result):
    return ",".join([date.strftime("%Y-%m-%d"), ric, measure_name, str(result)])


def cmd_compute(args: argparse.Namespace):

    if args.out:
        fout = open(args.out, "w")

    for root, _, files in os.walk(args.data_dir):
        for f in files:
            # skip those unsigned ones
            # TODO: .csv vs .csv.gz
            if "signed" not in f:
                continue

            path = os.path.join(root, f)
            ric, date = os.path.normpath(path).split(os.sep)[-2:]
            date = dt.fromisoformat(
                date.removesuffix(".csv")
                .removesuffix(".csv.gz")
                .removesuffix(".sorted")
                .removesuffix(".signed")
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
                    print(f"Computing bid-ask spread for {path}")
                    result = measures.bidaskspread.estimate(df)
                    print(
                        format_result(date, ric, measures.bidaskspread.name, result),
                        file=fout,
                    )

    fout.close()
