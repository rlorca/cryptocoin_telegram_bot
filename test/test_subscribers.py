from unittest import TestCase

from ctb.bot import Subscribers, Symbol


class TestSubscribers(TestCase):

    def setUp(self):
        self.subscribers = Subscribers()
        self.btc = Symbol("btc")
        self.bnb = Symbol("bnb")
        self.doge = Symbol("doge")


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

        btc = self.collect_subscribers(self.btc)

        self.assertSetEqual(set(["bob", "alice"]), btc)

        bnb = self.collect_subscribers(self.bnb)

        self.assertSetEqual(set(["bob"]), bnb)

        doge = self.collect_subscribers(self.doge)

        self.assertSetEqual(set(), doge)



    def collect_subscribers(self, symbol):

        result = set()

        for x in self.subscribers.for_symbol(symbol):
            result.add(x)

        return result









