#!/usr/bin/env python3
# Scrape option chain data from Yahoo Finance

import yfinance

import datetime
import json
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(filename)s:%(lineno)d:%(message)s')

data_path = os.environ.get('DATA_PATH', '/usr/local/share/scraper/data')

# TODO How to limit the underlying request rate?  Formerly used requests-ratelimiter:
#        # Maximum two requests per five seconds, ref: https://yfinance-python.org/advanced/caching.html
#        from requests_ratelimiter import LimiterSession
#        session = LimiterSession(per_second=2/5.0)
#        ...
#        ticker = yfinance.Ticker(ticker, session=session)

for ticker in os.environ.get('TICKERS', '').split(','):
    ticker = yfinance.Ticker(ticker)

    history = ticker.history(period='1d').to_json(orient='split')
    history_date = datetime.datetime.fromtimestamp(json.loads(history)['index'][0] / 1000).date()
    with open(f'{data_path}/{ticker.ticker.lower()}-{history_date.strftime("%Y%m%d")}.cjson', 'w') as file:
        file.write(history + '\n')

        for expiration in ticker.options:
            file.write(f'{{"type":"call","expiration":"{expiration}",' + \
                       ticker.option_chain(expiration).calls.to_json(orient='split')[1:] + '\n')

            file.write(f'{{"type":"put","expiration":"{expiration}",' + \
                       ticker.option_chain(expiration).puts.to_json(orient='split')[1:] + '\n')
    
    logging.info(f'{ticker.ticker.lower()} finished')
