import unittest
from gravitate.data_access import LocationGenericDao
from google.cloud.firestore import Transaction, transactional
from gravitate import context
import test.factory.model as model

db = context.Context.db


class LocationDAOTest(unittest.TestCase):

    # def setUp(self):
    #     self.user = User.from_dict(userDict)

    def testFindByAirportCode(self):
        result = LocationGenericDao().find_by_airport_code('LAX')
        self.assertNotEqual(None, result, 'Should return a result. ')

    def testSetWithTransaction(self):
        transaction = db.transaction()
        LocationGenericDao.set_with_transaction(transaction, model.getLocation(), model.mock1["locationFirestoreRef"])
        transaction.commit()

    def testSetWithTransactionTransactional(self):
        transaction = db.transaction()
        LocationGenericDao.set_with_transaction_transactional(transaction, model.getLocation(), model.mock1["locationFirestoreRef"])
        # transaction.commit()

