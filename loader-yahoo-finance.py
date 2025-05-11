# Load option chain data from Yahoo Finance

from collections import OrderedDict
from datetime import date, datetime
import json
import os
import re
from typing import Any, Callable, Iterator, List, Optional, TextIO, TypedDict

# Interface classes for use with other data sources later

class OptionData(TypedDict):
    type:          str
    expiration:    date
    strike:        float
    bid:           float
    ask:           float
    volume:        int
    open_interest: int

class Loader:
    def dates(self, ticker: str) -> Iterator[date]:
        pass

    def close(self, ticker: str, date: date) -> float:
        return None

    def options(self, ticker: str, expiration: date, date, calls_only: bool) -> List[OptionData]:
        return None

class YahooFinanceLoader(Loader):
    def __init__(self):
        self.__data_path = os.environ.get('DATA_PATH', './data/yahoo-finance')
        self.__fileobj_cache = self.Cache(dtor=lambda f: f.close())

    def __del__(self):
        for fileobj in self.__fileobj_cache.values():
            fileobj.close()

    def __get_fileobj(self, ticker: str, date: date) -> TextIO:
        basename = f'{ticker}-{date.strftime("%Y%m%d")}'
        if e := self.__fileobj_cache.get(basename):
            e.seek(0)
            return e

        rv = open(f'{self.__data_path}/{basename}.cjson')
        self.__fileobj_cache[basename] = rv
        return rv

    def dates(self, ticker: str) -> Iterator[date]:
        dates = []
        for filepath in os.listdir(self.__data_path):
            if m := re.match(fr'^{ticker}-(\d{{8}}).cjson$', filepath):
                dates += [m.group(1)]
        dates.sort()

        strtodate = lambda s: datetime.strptime(s, '%Y%m%d').date()
        for date in dates:
            yield strtodate(date)

    def close(self, ticker: str, date: date) -> float:
        fileobj = self.__get_fileobj(ticker, date)
        return json.loads(fileobj.readline())['data'][0][3]

    def options(self, ticker: str, expiration: date, date: date, calls_only: bool) -> List[OptionData]:
        fileobj = self.__get_fileobj(ticker, date)
        fileobj.readline()

        call_data, put_data = None, None
        expiration = expiration.strftime('%Y-%m-%d')
        for line in fileobj:
            data = json.loads(line)
            if data['expiration'] != expiration:
                continue
            if data['type'] == 'call':
                call_data = data
            elif data['type'] == 'put':
                put_data = data
            if call_data is not None and put_data is not None:
                break
        assert call_data is not None and put_data is not None

        options = []
        for entry in call_data['data']:
            _, _, strike, _, bid, ask, _, _, volume, open_interest = entry[:10]
            options += [{
                'type':          'call',
                'expiration':    expiration, 
                'strike':        strike,
                'bid':           bid,
                'ask':           ask,
                'volume':        volume,
                'open_interest': open_interest
            }]
        if not calls_only:
            for entry in put_data['data']:
                _, _, strike, _, bid, ask, _, _, volume, open_interest = entry[:10]
                options += [{
                    'type':          'put',
                    'expiration':    expiration, 
                    'strike':        strike,
                    'bid':           bid,
                    'ask':           ask,
                    'volume':        volume,
                    'open_interest': open_interest
                }]
        return options
    
    class Cache(OrderedDict):
        def __init__(self, size: int = 1000, dtor: Callable = None):
            OrderedDict.__init__(self)
            self.__size = size
            self.__dtor = dtor or (lambda e: None)
            self.__stats = {'hits':0, 'misses':0}

        def __del__(self):
            hits, misses = self.__stats['hits'], self.__stats['misses']
            if hits + misses > 0:
                print(f'cache stats: hits={hits} misses={misses} ratio={hits/(hits+misses):.2f}')

        def __setitem__(self, key, value):
            OrderedDict.__setitem__(self, key, value)
            while len(self) > self.__size:
                dtor(self.popitem(last=False))

        def get(self, key) -> Optional[Any]:
            rv = OrderedDict.get(self, key)
            self.__stats['hits' if rv else 'misses'] += 1
            return rv
