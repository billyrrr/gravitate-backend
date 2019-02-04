import unittest
from gravitate.data_access import LocationGenericDao
from google.cloud.firestore import Transaction, transactional
from gravitate import context
import test.store.model as model

db = context.Context.db


class LocationDAOTest(unittest.TestCase):

    def setUp(self):
        # self.user = User.from_dict(userDict)
        self.to_delete = list()

    def tearDown(self):
        for ref in self.to_delete:
            ref.delete()

    def testFindByAirportCode(self):
        result = LocationGenericDao().find_by_airport_code('LAX')
        self.assertNotEqual(None, result, 'Should return a result. ')

    def testSetWithTransaction(self):
        transaction = db.transaction()
        ref = model.mock1["locationFirestoreRef"]
        LocationGenericDao.set_with_transaction(transaction, model.getLocation(), ref)
        self.to_delete.append(ref)
        transaction.commit()

    def testSetWithTransactionTransactional(self):
        transaction = db.transaction()
        ref = model.mock1["locationFirestoreRef"]
        LocationGenericDao.set_with_transaction_transactional(transaction, model.getLocation(), ref)
        self.to_delete.append(ref)
        # transaction.commit()

