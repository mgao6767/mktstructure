# mktstructure

A simple command-line tool to download data from Refinitiv Tick History and compute some market microstructure measures.

## Installation

``` bash
pip install mktstructure
```

After installation, use `-h` or `--help` to see the usage instruction:

``` bash
$ mktstructure -h
usage: mktstructure [OPTION]...

Download data from Refinitiv Tick History and compute some market microstructure measures.

optional arguments:
  -h, --help       show this help message and exit
  -v, --version    show program's version number and exit
  -u user          DataScope username
  -p password      DataScope password
  -b begin         begin UTC date (YYYY-MM-DD)
  -e end           end UTC date (YYYY-MM-DD)
  -o out           output file path
  --ric [RIC ...]  RIC of securities to process
  --sp500          if set, process all S&P500 components (extending RIC list, if any)
  --parse          if set, parse the downloaded raw data to output data directory
  --data_dir dir   output data directory (used when --parse is set)
```

## Usage examples

### Simple use cases

Download the tick history of Google from 2022-01-01 to 2022-02-01, saved as `out.csv.gz` in the current working directory:

```bash
mktstructure -u XXXXXX -p XXXXXX --ric GOOG.OQ -b 2022-01-01 -e 2022-02-01 -o out.csv.gz
```

Download the tick history of Google and Apple from 2022-01-01 to 2022-02-01, saved as `out.csv.gz` in the current working directory:

```bash
mktstructure -u XXXXXX -p XXXXXX --ric GOOG.OQ AAPL.OQ -b 2022-01-01 -e 2022-02-01 -o out.csv.gz
```

### Most common use case

Download the tick history of all S&P500 component stocks from 2022-01-01 to 2022-02-01, saved as `sp500.csv.gz` in the current working directory:

```bash
mktstructure -u XXXXXX -p XXXXXX --sp500 -b 2022-01-01 -e 2022-02-01 -o sp500.csv.gz
```

Or further, download and parse the downloaded data:

```bash
mktstructure -u XXXXXX -p XXXXXX --sp500 -b 2022-01-01 -e 2022-02-01 -o sp500.csv.gz --parse --datadir "./data"
```

After everything's completed, the daily tick history will be stored in `./data` folder as specified by the `--data_dir` option.

```powershell
PS C:\Users\mgao\Documents\GitHub\mkt-microstructure> ls .\data\


    Directory: C:\Users\mgao\Documents\GitHub\mkt-microstructure\data


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----         6/03/2022   3:30 PM                A.N
d-----         6/03/2022   3:30 PM                AAL.OQ
d-----         6/03/2022   3:31 PM                AAP.N
d-----         6/03/2022   3:31 PM                AAPL.OQ

...

d-----         6/03/2022   3:51 PM                ZBH.N
d-----         6/03/2022   3:51 PM                ZBRA.OQ
d-----         6/03/2022   3:51 PM                ZION.OQ
d-----         6/03/2022   3:51 PM                ZTS.N
```
