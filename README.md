# mktstructure

A simple command-line tool to download data from Refinitiv Tick History and compute some market microstructure measures.

## Installation

You can install `mktstructure` via `pip`:

``` bash
pip install mktstructure
```

## Quick Start

Use `-h` or `--help` to see the usage instruction:

``` bash
$ mktstructure -h
usage: mktstructure [OPTION]...

Download data from Refinitiv Tick History and compute some market microstructure measures.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit

Sub-commands:
  Choose one from the following. Use `mktstructure subcommand -h` to see help for each sub-command.

  {download,clean,classify,compute}
    download            Download data from Refinitiv Tick History
    clean               Clean downloaded data
    classify            Classify ticks into buy and sell orders
    compute             Compute market microstructure measures
```

### 1. Download data

Let's download the tick history for all S&P500 component stocks from Jan 1, 2022, to Jan 31, 2022:

``` bash
mktstructure download -u {username} -p {password} --sp500 --parse --data_dir "./data" -b 2022-01-01 -e 2022-01-31
```

where `{username}` and `{password}` are the login credentials of Refinitiv DataScope Select.

Note that we set the `--parse` flag to parse the downloaded data (gzip) into csv files by stock and date into the `./data` folder.

### 2. Clean data

Then we clean the downloaded and parsed data in the `./data` folder: sorting by time, removing duplicates, etc.

``` bash
mktstructure clean --all --data_dir "./data" --replace
```

The ``--replace`` flag, if set, asks the program to replace the data file with the cleaned one to save disk space.

### 3. Classify trade directions

Use the `classify` subcommand to classify trades into buys and sells by the Lee and Ready (1991) algorithm.

``` bash
mktstructure classify --all --data_dir "./data"
```

### 4. Compute

Lastly, use the `compute` subcommand to compute specified market microstructure measures:

``` bash
mktstructure compute --all --data_dir "./data" --out bidaskspread.csv --bid_ask_spread
```

## Note

This tool is still a work in progress. Some breaking changes may be expected but will be kept minimal.
