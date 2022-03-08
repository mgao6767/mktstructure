import argparse
import os

from .utils import _sort_and_rm_duplicates


def cmd_clean(args: argparse.Namespace):

    # sort by time and remove duplicates
    if args.all:
        for root, dirs, files in os.walk(args.data_dir):
            for f in files:
                path = os.path.join(root, f)
                if os.path.isfile(path):
                    print(f"Cleaning {path}")
                    _sort_and_rm_duplicates(path, replace=True)
