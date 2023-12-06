import argparse
import pandas as pd

from .parx import parx
from .lee_ready import lee_and_ready
from .utils import process_files, filter_quotes, transform_taq


def classify(path):
    df = pd.read_csv(path)
    df = transform_taq(df)

    df_signed = lee_and_ready(df)
    df_signed.to_csv(path.replace(".sorted.csv.gz",
                     ".signed-trades.csv.gz"), compression="gzip")

    df_quotes = filter_quotes(df)
    df_quotes.to_csv(path.replace(".sorted.csv.gz",
                     ".quotes.csv.gz"), compression="gzip")


def cmd_classify(args: argparse.Namespace):
    """
    Classify trade directions on the sorted data.
    Create "2020-01-01.signed-trades.csv.gz" in the same folder.
    Also create quotes.
    """
    files = process_files(
        args.data_dir, file_pattern="????-??-??.sorted.csv.gz")
    parx(classify, [path for _, _, path in files], workers=args.threads)
