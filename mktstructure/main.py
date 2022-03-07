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
    # subparsers
    subparsers = parser.add_subparsers(
        title="Sub-commands",
        dest="command",
        description="Choose one from the following. Use `mktstructure subcommand -h` to see help for each sub-command.",
    )
    parser_download = subparsers.add_parser(
        "download",
        description="Download data from Refinitiv Tick History",
        help="Download data from Refinitiv Tick History",
    )
    parser_clean = subparsers.add_parser(
        "clean",
        description="Clean the data in the data directory",
        help="Clean downloaded data",
    )
    parser_classify = subparsers.add_parser(
        "classify",
        description="Classify ticks into buy and sell orders using Lee and Ready (1991) algorithm",
        help="Classify ticks into buy and sell orders",
    )
    parser_compute = subparsers.add_parser(
        "compute",
        description="Compute specified measures",
        help="Compute market microstructure measures",
    )

    # subparser for `download` subcommand
    parser_download.add_argument(
        "-u",
        metavar="user",
        help="DataScope username",
    )
    parser_download.add_argument(
        "-p",
        metavar="password",
        help="DataScope password",
    )
    parser_download.add_argument(
        "-b",
        metavar="begin",
        default="2021-02-15",
        help="begin UTC date (YYYY-MM-DD)",
    )
    parser_download.add_argument(
        "-e",
        metavar="end",
        default="2021-02-28",
        help="end UTC date (YYYY-MM-DD)",
    )
    parser_download.add_argument(
        "-o",
        metavar="out",
        default="out.csv.gz",
        help="output file path",
    )
    parser_download.add_argument(
        "--ric",
        nargs="*",
        default=[],
        help="RIC of securities to process",
    )
    parser_download.add_argument(
        "--sp500",
        default=False,
        const=True,
        action="store_const",
        help="if set, process all S&P500 components (extending RIC list, if any)",
    )
    parser_download.add_argument(
        "--parse",
        default=False,
        const=True,
        action="store_const",
        help="if set, parse the downloaded raw data to output data directory",
    )
    parser_download.add_argument(
        "--data_dir",
        metavar="dir",
        default="./data",
        help="output data directory (used when --parse is set)",
    )

    # parser for `clean` subcommand
    parser_clean.add_argument(
        "--ric",
        nargs="*",
        default=[],
        help="RIC of securities to clean",
    )
    parser_clean.add_argument(
        "-b",
        metavar="begin",
        default="2021-02-15",
        help="begin UTC date (YYYY-MM-DD)",
    )
    parser_clean.add_argument(
        "-e",
        metavar="end",
        default="2021-02-28",
        help="end UTC date (YYYY-MM-DD)",
    )
    parser_clean.add_argument(
        "--data_dir",
        metavar="dir",
        help="data directory",
        required=True,
    )
    parser_clean.add_argument(
        "--all",
        default=False,
        const=True,
        action="store_const",
        help="if set, clean all data in the data director",
    )

    # parser for `classify` subcommand
    parser_classify.add_argument(
        "--ric",
        nargs="*",
        default=[],
        help="RIC of securities to clean",
    )
    parser_classify.add_argument(
        "-b",
        metavar="begin",
        default="2021-02-15",
        help="begin UTC date (YYYY-MM-DD)",
    )
    parser_classify.add_argument(
        "-e",
        metavar="end",
        default="2021-02-28",
        help="end UTC date (YYYY-MM-DD)",
    )
    parser_classify.add_argument(
        "--data_dir",
        metavar="dir",
        help="data directory",
        required=True,
    )
    parser_classify.add_argument(
        "--all",
        default=False,
        const=True,
        action="store_const",
        help="if set, classify all data in the data director",
    )

    return parser


def cmd_download(args: argparse.Namespace):

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


def cmd_clean(args: argparse.Namespace):
    from .utils import _sort_and_rm_duplicates

    # sort by time and remove duplicates
    if args.all:
        for root, dirs, files in os.walk(args.data_dir):
            for f in files:
                path = os.path.join(root, f)
                if os.path.isfile(path):
                    print(f"Cleaning {path}")
                    _sort_and_rm_duplicates(path, replace=False)


def cmd_classify(args: argparse.Namespace):
    pass


def cmd_compute(args: argparse.Namespace):
    pass


def main():
    parser = init_argparse()
    args = parser.parse_args()

    if args.command == "download":
        cmd_download(args)

    if args.command == "clean":
        cmd_clean(args)

    if args.command == "classify":
        cmd_classify(args)

    if args.command == "compute":
        cmd_compute(args)


if __name__ == "__main__":
    main()
