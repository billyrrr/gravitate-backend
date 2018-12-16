from unittest import TestCase
from data_access.strategy import TransactionStrategy
from functools import partial

def exampleExecutable(a, b):
    print("a: {}, b: {}".format(a, b))

class TestTransactionStrategy(TestCase):

    def setUp(self):
        self.ts = TransactionStrategy()

    def testAddStep(self):
        step = partial(exampleExecutable, "operations")
        self.ts.addStep(step)
        self.assertEqual(self.ts.strategies, [step])

class TestTransactionStrategyExecuteAll(TestCase):

    def setUp(self):
        self.ts = TransactionStrategy()
        step = partial(exampleExecutable, "operations")
        self.ts.addStep(step)

    def testExecuteAll(self):
        self.ts.executeAll("provided_transaction")
        self.fail()