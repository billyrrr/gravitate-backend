"""
Strategy pattern for Firestore transactions
"""


class TransactionStrategy:
    strategies = None

    def __init__(self):
        self.strategies = list()

    def addStep(self, strategy):
        self.strategies.append(strategy)

    def _executeAll(stragegies: list):
        for strategy in stragegies:
            strategy()
