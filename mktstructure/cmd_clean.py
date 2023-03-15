import argparse
import os
from datetime import datetime as dt
from concurrent.futures import as_completed, ProcessPoolExecutor
import tqdm

from .utils import _sort_and_rm_duplicates


def clean(path, args):
    for root, _, files in os.walk(path):
        for f in files:
            path = os.path.join(root, f)
            if os.path.isfile(path):
                _sort_and_rm_duplicates(path, replace=args.replace)


def cmd_clean(args: argparse.Namespace):
    # sort by time and remove duplicates

    if args.all:
        _, rics, _ = next(os.walk(args.data_dir))
        workers = min(os.cpu_count(), args.threads)
        progress = tqdm.tqdm(total=len(rics))
        with ProcessPoolExecutor(workers) as exe:
            fs = [
                exe.submit(clean, os.path.join(args.data_dir, ric), args)
                for ric in rics
            ]
            for _ in as_completed(fs):
                progress.update()
    else:
        for root, _, files in os.walk(args.data_dir):
            for f in files:
                path = os.path.join(root, f)
                ric, date = os.path.normpath(path).split(os.sep)[-2:]

                if not ric in args.ric:
                    continue
                date = dt.fromisoformat(
                    date.removesuffix(".csv")
                    .removesuffix(".csv.gz")
                    .removesuffix(".sorted")
                )
                if not (dt.fromisoformat(args.b) <= date <= dt.fromisoformat(args.e)):
                    continue

                if os.path.isfile(path):
                    print(f"Cleaning {path}")
                    _sort_and_rm_duplicates(path, replace=args.replace)
