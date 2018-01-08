from unittest import TestCase
from unittest.mock import Mock

from ctb.quote import QuoteService, CoinSymbol, QuoteFetcher, CoinQuote


class TestSubscribers(TestCase):

    def setUp(self):

        self.fetcher = Mock(QuoteFetcher.fetch)
        self.service = QuoteService(self.fetcher)
        self.btc_symbol = CoinSymbol('btc')

    def test_empty(self):
        self.assertIsNone(self.service.latest_quote(self.btc_symbol))

    def test_quote_update(self):

        quote = CoinQuote({
            "symbol": "BTC",
            "price_usd": "1000",
            "percent_change_1h": "10",
            "percent_change_24h": "-5",
            "last_updated": 100
        })

        self.fetcher.return_value = [quote]

        self.assertIn(quote, self.service.updated_quotes())

        # second call, nothing will be returned as the quote has the same timestamp
        self.assertNotIn(quote, self.service.updated_quotes())

        # now there will be an updated version of the quote

        new_quote = CoinQuote({
            "symbol": "BTC",
            "price_usd": "1001",
            "percent_change_1h": "11",
            "percent_change_24h": "-4",
            "last_updated": 200
        })

        self.fetcher.return_value = [new_quote]

        # the new quote will now be returned
        self.assertIn(new_quote, self.service.updated_quotes())

