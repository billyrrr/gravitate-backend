import unittest
from gravitate.data_access import LocationGenericDao
from google.cloud.firestore import Transaction, transactional
from gravitate import config
import test.factory.model as model

db = config.Context.db


class LocationDAOTest(unittest.TestCase):

    # def setUp(self):
    #     self.user = User.from_dict(userDict)

    def testFindByAirportCode(self):
        result = LocationGenericDao().findByAirportCode('LAX')
        self.assertNotEqual(None, result, 'Should return a result. ')

    def testSetWithTransaction(self):
        transaction = db.transaction()
        LocationGenericDao.setWithTransaction(transaction, model.getLocation(), model.mock1["locationFirestoreRef"])
        transaction.commit()

    def testSetWithTransactionTransactional(self):
        transaction = db.transaction()
        LocationGenericDao.setWithTransactionTransactional(transaction, model.getLocation(), model.mock1["locationFirestoreRef"])
        # transaction.commit()

