"""
Coin-related services and types.
"""

import logging
from typing import Generator, Set

import requests

logging.getLogger(__name__).addHandler(logging.NullHandler())

class CoinSymbol:
    """
    Coin Symbol.
    """

    def __init__(self, symbol_str):
        self.value = symbol_str.upper()

    def __str__(self):
        return self.value

    def __eq__(self, other):
        return other and self.value == other.value

    def __hash__(self):
        return hash(self.value)


class CoinQuote(object):
    """
    Quote for a coin.
    """

    def __init__(self, values):
        self.values = values
        self.symbol = CoinSymbol(values["symbol"])

    def __getattr__(self, item):
        return object.__getattribute__(self, "values")[item]

    def is_newer(self, other):
        return not other or \
               int(self.last_updated) > int(other.last_updated)


class QuoteFetcher:

    @staticmethod
    def fetch() -> [CoinQuote]:
        """
        Get current quotes from API.
        """
        response = requests.get("https://api.coinmarketcap.com/v1/ticker/")

        if response.status_code == 200:
            return map(CoinQuote, response.json())

        logging.error("Wrong status code received: %d", response.status_code)
        return []


class QuoteService:

    def __init__(self, fetcher=QuoteFetcher.fetch):
        self._fetcher = fetcher
        self._latest_quotes = {}

    def coins_available(self) -> Set[CoinSymbol]:
        return self._latest_quotes.keys()

    def latest_quote(self, symbol: CoinSymbol) -> CoinQuote:
        """
        Get latest quote for a given coin.
        """
        return self._latest_quotes.get(symbol, None)

    def updated_quotes(self) -> Generator[CoinQuote, None, None]:
        """
        Get the quotes that were updated since the last call.
        """
        for fetch in self._fetcher():

            latest = self.latest_quote(fetch.symbol)

            if fetch.is_newer(latest):
                self._latest_quotes[fetch.symbol] = fetch
                yield fetch
