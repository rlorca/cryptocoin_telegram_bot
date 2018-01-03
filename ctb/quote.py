import logging
from threading import Thread, Event
import requests

logging.getLogger(__name__).addHandler(logging.NullHandler())


class Coin(object):
    def __init__(self, values):
        self.values = values

    def __getattr__(self, item):
        return object.__getattribute__(self, "values")[item]

    def is_newer(self, other):

        if other:
            return int(self.last_updated) > int(other.last_updated)
        else:
            return True


class QuoteLoader:

    def __enter__(self):
        self.latest_quotes = self.fetch()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def latest(self, symbol):
        return self.latest_quotes.get(symbol.upper(), None)

    @staticmethod
    def fetch():
        response = requests.get("https://api.coinmarketcap.com/v1/ticker/")

        if response.status_code == 200:
            return {c.symbol.upper(): c for c in map(Coin, response.json())}
        else:
            logging.error("Wrong status code received: %d", response.status_code)
            return []

    def diff(self):

        for fetch in self.fetch().values():

            latest = self.latest_quotes.get(fetch.symbol, None)

            if fetch.is_newer(latest):
                self.latest_quotes[fetch.symbol] = fetch
                yield fetch


class LoadScheduler(Thread):

    def __init__(self, interval, loader, callback):
        Thread.__init__(self)
        self.stopped = Event()
        self.interval = interval
        self.callback = callback
        self.setDaemon(True)
        self.loader = loader

    def stop(self):
        self.stopped.set()

    def run(self):

        while not self.stopped.wait(self.interval):

            logging.debug("Updating quotes")

            for q in self.loader.diff():
                self.callback(q)

            logging.debug("Update terminated")
