import argparse
import os
import gzip
import shutil

from mktstructure import __description__, __version__
from .trth import Connection
from .utils import extract_index_components_ric
from .utils import SP500_RIC, NASDAQ_RIC, NYSE_RIC
from .trth_parser import parse_to_data_dir


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION]...",
        description=__description__,
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"{parser.prog} version {__version__}",
    )
    parser.add_argument(
        "-u",
        metavar="user",
        help="DataScope username",
    )
    parser.add_argument(
        "-p",
        metavar="password",
        help="DataScope password",
    )
    parser.add_argument(
        "-b",
        metavar="begin",
        default="2021-02-15",
        help="begin UTC date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "-e",
        metavar="end",
        default="2021-02-28",
        help="end UTC date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "-o",
        metavar="out",
        default="out.csv.gz",
        help="output file path",
    )
    parser.add_argument(
        "--ric",
        nargs="*",
        default=[],
        help="RIC of securities to process",
    )
    parser.add_argument(
        "--sp500",
        default=False,
        const=True,
        action="store_const",
        help="if set, process all S&P500 components (extending RIC list, if any)",
    )
    parser.add_argument(
        "--parse",
        default=False,
        const=True,
        action="store_const",
        help="if set, parse the downloaded raw data to output data directory",
    )
    parser.add_argument(
        "--data_dir",
        metavar="dir",
        default="./data",
        help="output data directory (used when --parse is set)",
    )
    return parser


def main():
    parser = init_argparse()
    args = parser.parse_args()

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

    data = trth.get_table(args.ric, start_date, end_date)

    print(f"Saving data to {args.o}...")

    trth.save_results(data, args.o)

    print("Downloading finished.")

    if args.parse:

        print("Decompressing downloaded data.")
        with gzip.open(args.o, "rb") as fin, open("__tmp.csv", "wb") as fout:
            shutil.copyfileobj(fin, fout)

        print("Parsing downloaded raw data.")
        parse_to_data_dir("__tmp.csv", args.data_dir, "1")

        os.remove("__tmp.csv")


if __name__ == "__main__":
    main()
