import argparse
import os
from datetime import datetime as dt
from concurrent.futures import as_completed, ProcessPoolExecutor
import tqdm
import pandas as pd

from .utils import lee_and_ready


def classify(path):
    for root, _, files in os.walk(path):
        for f in files:
            # skip those signed ones
            if "signed" in f:
                continue
            # work on only sorted files
            if not ".sorted.csv.gz" in f:
                continue
            p = os.path.join(root, f)

            if os.path.isfile(p):
                df = pd.read_csv(p)
                df_signed = lee_and_ready(df)
                df_signed.to_csv(p.replace(".csv", ".signed.csv"))


def cmd_classify(args: argparse.Namespace):
    if args.all:
        _, rics, _ = next(os.walk(args.data_dir))
        workers = min(os.cpu_count(), args.threads)
        progress = tqdm.tqdm(total=len(rics))
        with ProcessPoolExecutor(workers) as exe:
            fs = [
                exe.submit(classify, os.path.join(args.data_dir, ric)) for ric in rics
            ]
            for _ in as_completed(fs):
                progress.update()
    else:
        # if `--all` flag is set
        for root, _, files in os.walk(args.data_dir):
            for f in files:
                if "signed" in f:
                    continue
                if not ".sorted.csv.gz" in f:
                    continue

                path = os.path.join(root, f)
                ric, date = os.path.normpath(path).split(os.sep)[-2:]

                if ric not in args.ric:
                    continue
                date = dt.fromisoformat(
                    date.removesuffix(".csv")
                    .removesuffix(".csv.gz")
                    .removesuffix(".sorted")
                )
                if not (dt.fromisoformat(args.b) <= date <= dt.fromisoformat(args.e)):
                    continue
