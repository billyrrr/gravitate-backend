"""
Strategy pattern for Firestore transactions
"""


def _executeAll(stragegies: list, transaction):
    for strategy in stragegies:
        strategy(transaction)

class TransactionStrategy:
    strategies = None

    def __init__(self):
        self.strategies = list()

    def addStep(self, strategy):
        self.strategies.append(strategy)

    def executeAll(self, transaction):
        _executeAll(self.strategies, transaction)

