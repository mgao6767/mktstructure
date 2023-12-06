import argparse
from functools import partial

from .utils import _sort_and_rm_duplicates, process_files
from .parx import parx


def cmd_clean(args: argparse.Namespace):
    """
    Sort and remove duplicates
    If args.replace flag is set, replace the file.
    If not, create new file like "2020-01-01.signed.csv.gz" in the same folder.
    """
    files = process_files(args.data_dir, file_pattern="????-??-??.csv.gz")
    func_clean = partial(_sort_and_rm_duplicates, replace=args.replace)
    parx(func_clean, [path for _, _, path in files], workers=args.threads)
