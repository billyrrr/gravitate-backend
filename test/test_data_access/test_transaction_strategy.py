from functools import partial
from unittest import TestCase, skip

from gravitate.data_access.strategy import TransactionStrategy


def exampleExecutable(a, b):
    print("a: {}, b: {}".format(a, b))


class TestTransactionStrategy(TestCase):

    def setUp(self):
        self.ts = TransactionStrategy()

    def testAddStep(self):
        step = partial(exampleExecutable, "operations")
        self.ts.add_step(step)
        self.assertEqual(self.ts.strategies, [step])


class TestTransactionStrategyExecuteAll(TestCase):

    def setUp(self):
        self.ts = TransactionStrategy()
        step = partial(exampleExecutable, "operations")
        self.ts.add_step(step)

    @skip("not yet implemented")
    def testExecuteAll(self):
        self.ts.execute_all("provided_transaction")
        self.fail()
