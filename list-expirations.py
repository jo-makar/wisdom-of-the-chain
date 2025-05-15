#!/usr/bin/env python3
# List expirations

import importlib
Loader = importlib.import_module('loader-yahoo-finance').YahooFinanceLoader

import argparse
import datetime
from typing import List, Set

parser = argparse.ArgumentParser()
parser.add_argument('ticker')
strtodate = lambda s: datetime.datetime.strptime(s, '%Y-%m-%d').date()
parser.add_argument('--start-date', '-s', type=strtodate)
parser.add_argument('--end-date', '-e', type=strtodate)

args = parser.parse_args()
if args.start_date and args.end_date:
    assert args.start_date < args.end_date

loader = Loader()
expirations: Set[datetime.date] = set()
for date in loader.dates(args.ticker):
    if args.start_date and date < args.start_date:
        continue
    if args.end_date and date >= args.end_date:
        break
    expirations.update(loader.expirations(args.ticker, date))

datetostr = lambda d: d.strftime('%Y-%m-%d')
expirations: List[datetime.date] = sorted(list(expirations))
for expiration in expirations:
    print(datetostr(expiration))
