"""
Strategy pattern for Firestore transactions
"""


def _execute_all(stragegies: list, transaction):
    for strategy in stragegies:
        strategy(transaction)

class TransactionStrategy:
    strategies = None

    def __init__(self):
        self.strategies = list()

    def add_step(self, strategy):
        self.strategies.append(strategy)

    def execute_all(self, transaction):
        _execute_all(self.strategies, transaction)

