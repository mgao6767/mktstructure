import argparse
import gzip
import os
from shutil import copyfileobj

from .utils import extract_index_components_ric
from .utils import SP500_RIC, NASDAQ_RIC, NYSE_RIC
from .trth import Connection


def cmd_download_mktdepth(args: argparse.Namespace):

    start_date = f"{args.b}T00:00:00.000Z"
    end_date = f"{args.e}T00:00:00.000Z"

    print("Connecting to TRTH...")
    trth = Connection(args.u, args.p, progress_callback=print)

    if args.sp500:
        args.ric.extend(
            extract_index_components_ric(
                trth.get_index_components([SP500_RIC], start_date, end_date),
                mkt_index=[SP500_RIC],
            )
        )

    data = trth.get_table_mktdepth(args.ric, start_date, end_date)

    print(f"Saving data to {args.o}...")

    trth.save_results(data, args.o)

    print("Downloading finished.")
