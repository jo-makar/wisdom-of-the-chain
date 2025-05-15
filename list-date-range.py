#!/usr/bin/env python3
# List date range

import importlib
Loader = importlib.import_module('loader-yahoo-finance').YahooFinanceLoader

import argparse
import datetime
from typing import List, Set

parser = argparse.ArgumentParser()
parser.add_argument('ticker')
args = parser.parse_args()

loader = Loader()
date_iter = loader.dates(args.ticker)
start_date = next(date_iter)
end_date = start_date
for date in date_iter:
    end_date = date

datetostr = lambda d: d.strftime('%Y-%m-%d')
print(datetostr(start_date))
print(datetostr(end_date))
