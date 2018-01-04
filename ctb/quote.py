import logging
from typing import Generator

import requests

logging.getLogger(__name__).addHandler(logging.NullHandler())


class Coin(object):
    def __init__(self, values):
        self.values = values

    def __getattr__(self, item):
        return object.__getattribute__(self, "values")[item]

    def is_newer(self, other):

        return not other or \
               int(self.last_updated) > int(other.last_updated)

class QuoteService:

    def __init__(self):
        self.loader = QuoteLoader()
        self.latest_quotes = {}

    def latest_quote(self, symbol) -> Coin:
            return self.latest_quotes.get(symbol.upper(), None)

    def updated_quotes(self) -> Generator[Coin, None, None]:

        for fetch in self.loader.fetch():

            latest = self.latest_quote(fetch.symbol)

            if fetch.is_newer(latest):
                self.latest_quotes[fetch.symbol] = fetch
                yield fetch


class QuoteLoader:

    @staticmethod
    def fetch() -> [Coin]:
        response = requests.get("https://api.coinmarketcap.com/v1/ticker/")

        if response.status_code == 200:
            return map(Coin, response.json())
        else:
            logging.error("Wrong status code received: %d", response.status_code)
            return []