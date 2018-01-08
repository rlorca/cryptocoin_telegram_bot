from functools import reduce
from unittest import TestCase

from ctb.bot import Subscribers, CoinSymbol


class TestSubscribers(TestCase):

    def setUp(self):
        self.subscribers = Subscribers()
        self.btc = CoinSymbol("btc")
        self.bnb = CoinSymbol("bnb")
        self.doge = CoinSymbol("doge")

    def test_successfull_removal(self):
        self.subscribers.add(self.btc, "bob")
        self.assertTrue(self.subscribers.remove(self.btc, "bob"))

    def test_failed_removal(self):
        self.subscribers.add(self.btc, "bob")
        self.assertFalse(self.subscribers.remove(self.btc, "alice"))

    def test_unkwnown_coin(self):
        self.assertFalse(self.subscribers.remove(self.doge, "alice"))

    def test_follow(self):
        self.subscribers.add(self.btc, "bob")
        self.subscribers.add(self.bnb, "bob")
        self.subscribers.add(self.btc, "alice")

        self.assertSetEqual(set(["bob", "alice"]),
                            self.collect_subscribers(self.btc))

        self.assertSetEqual(set(["bob"]),
                            self.collect_subscribers(self.bnb))

        self.assertSetEqual(set(),
                            self.collect_subscribers(self.doge))

    def collect_subscribers(self, symbol):

        def add(acc, it):
            acc.add(it)
            return acc

        return reduce(add,
                      self.subscribers.for_symbol(symbol),
                      set())







