import os
import glob
import gzip
import shutil
from datetime import datetime
import json
from typing import List, Dict, Tuple
import pandas as pd
import numpy as np
from .request_templates import INDEX_COMPONENTS, INTRADAY_TICKS, INTRADAY_MARKET_DEPTH


SP500_RIC = "0#.SPX"
NASDAQ_RIC = "0#.NDX"
NYSE_RIC = "0#.NYA"


def extract_index_components_ric(chain_result_json, mkt_index: List[str]):
    """
    Example json result:
    https://developers.refinitiv.com/thomson-reuters-tick-history-trth/thomson-reuters-tick-history-trth-rest-api/learning?content=13754&type=learning_material_item
    """
    if isinstance(chain_result_json, str):
        chain_result = json.loads(chain_result_json)
    elif isinstance(chain_result_json, dict):
        chain_result = chain_result_json
    vals: List[Dict] = chain_result.get("value")
    securities = set()
    for val in vals:
        identifier = val.get("Identifier")
        if identifier in mkt_index:
            constituents = val.get("Constituents")
            for security in constituents:
                ric: str = security.get("Identifier")
                if ric and not ric.startswith("."):
                    securities.add(ric)
    return list(securities)


def make_request_index_components(mkt_index: List[str], date_start, date_end):
    request = INDEX_COMPONENTS.copy()
    request["Request"]["ChainRics"] = mkt_index
    request["Request"]["Range"]["Start"] = date_start
    request["Request"]["Range"]["End"] = date_end
    return json.dumps(request)


def make_request_tick_history(rics: List[str], date_start, date_end):
    request = INTRADAY_TICKS.copy()
    request["ExtractionRequest"]["IdentifierList"]["InstrumentIdentifiers"] = [
        {"Identifier": ric, "IdentifierType": "Ric"} for ric in rics
    ]
    request["ExtractionRequest"]["Condition"]["QueryStartDate"] = date_start
    request["ExtractionRequest"]["Condition"]["QueryEndDate"] = date_end
    return request


def make_request_tick_history_market_depth(rics: List[str], date_start, date_end):
    request = INTRADAY_MARKET_DEPTH.copy()
    request["ExtractionRequest"]["IdentifierList"]["InstrumentIdentifiers"] = [
        {"Identifier": ric, "IdentifierType": "Ric"} for ric in rics
    ]
    request["ExtractionRequest"]["Condition"]["QueryStartDate"] = date_start
    request["ExtractionRequest"]["Condition"]["QueryEndDate"] = date_end
    return request


def transform_taq(df: pd.DataFrame) -> pd.DataFrame:
    # Convert to pd.DatetimeIndex to preserve nanoseconds.
    df["Date-Time"] = pd.DatetimeIndex(df["Date-Time"])
    # Get GMT Offset
    offset = np.timedelta64(df["GMT Offset"].iloc[0], "h")
    # Convert from GMTUTC to local time.
    df["Date-Time"] = df["Date-Time"] + offset
    # Set local time as index.
    df.set_index("Date-Time", inplace=True)
    # Keep only trades/quotes during normal trading hours.
    # TODO: Check RIC and get trading hours for non US exchanges.
    # without `.copy()` there is hidden chaining causing `SettingSettingWithCopyWarning` warning
    return df.between_time(start_time="09:30", end_time="16:00").copy()


def filter_quotes(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["Type"] == "Quote"]


def _sort_and_rm_duplicates(data_path, replace=True):
    """
    Remove trades/quotes with same Bid/Ask/Volume/Price at the same nanosecond.
    It is highly unlikely that two quotes/trades of exactly the same parameters happen at the same nanosecond.
    """
    # Parse_dates here will result in loss of nanosecond precision!
    df = pd.read_csv(data_path)
    # obs = len(df.index)
    # Drop duplicates first before converting Date-Time to DatetimeIndex, otherwise it'll be ignored.
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.drop_duplicates.html
    df.drop_duplicates(inplace=True)
    # This conversion preserves the nanoseconds.
    df["Date-Time"] = pd.DatetimeIndex(df["Date-Time"])
    df.set_index(["Date-Time"], inplace=True)
    df.sort_index(inplace=True)
    # new_len = len(df.index)
    df.to_csv(
        data_path if replace else f"{data_path.replace('.csv', '.sorted.csv')}",
        compression="gzip",
        mode="w",
    )


def process_files(data_folder: str, file_pattern="*.signed.csv") -> List[Tuple[str, str, str]]:
    """
    Processes files in a given data folder, extracting the RIC, date, and file path for each .csv.gz file.

    Args:
        data_folder (str): The path to the data folder containing subdirectories named after RIC codes.
        file_pattern (str): The file pattern to match. Defaults to "*.signed.csv".

    Returns:
        List[Tuple[str, str, str]]: A list of tuples, each containing the RIC code, date, and file path.
    """
    # This will hold the result
    result = []

    # Iterate over all subdirectories in the data_folder
    for ric_folder in os.listdir(data_folder):
        ric_folder_path = os.path.join(data_folder, ric_folder)

        # Check if it's a directory
        if os.path.isdir(ric_folder_path):
            # Use glob to find all .csv.gz files in this directory
            for file_path in glob.glob(os.path.join(ric_folder_path, file_pattern)):
                # Extract the date from the file name
                file_name = os.path.basename(file_path)
                date_str = file_name.split('.')[0]
                try:
                    # Check if the date string is valid
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                    date_str = date_obj.isoformat()
                    # Add the RIC, date, and path to the result
                    result.append((ric_folder, date_str, file_path))
                except ValueError:
                    # If the date is not valid, skip this file
                    continue

    return result


def gzip_file(file_path: str):
    """
    Compresses a file using gzip and stores it in the same folder.

    Args:
        file_path (str): The path of the file to be compressed.
    """
    compressed_file_path = file_path + '.gz'

    with open(file_path, 'rb') as f_in:
        with gzip.open(compressed_file_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    print(f"Compressed file stored at {compressed_file_path}")


def read_gzipped_file(file_path: str) -> str:
    """
    Reads the content of a gzipped file and returns it.

    Args:
        file_path (str): The path of the gzipped file to be read.

    Returns:
        str: The content of the gzipped file.
    """
    try:
        with gzip.open(file_path, 'rt') as f:
            return f.read()
    except OSError as e:
        print(f"Error: {e.strerror}. Could not read file {file_path}.")
        return ""


def delete_file(file_path: str):
    """
    Deletes a file specified by the file path.

    Args:
        file_path (str): The path of the file to be deleted.
    """
    try:
        os.remove(file_path)
        print(f"File {file_path} has been deleted.")
    except OSError as e:
        print(f"Error: {e.strerror}. File {file_path} could not be deleted.")
