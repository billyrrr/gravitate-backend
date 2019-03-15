import unittest

import test.store.model as model
from gravitate import context
from gravitate.data_access import LocationGenericDao
from gravitate.models import Location
from test import scripts as setup_scripts

db = context.Context.db


class LocationDAOTest(unittest.TestCase):

    def setUp(self):
        # self.user = User.from_dict(userDict)
        self.to_delete = list()

        self.refs_to_delete = list()

        self.cl = setup_scripts.SetUpTestDatabase()
        self.cl.clear_before()

        self.pl = setup_scripts.scripts.populate_locations.PopulateLocationCommand()
        self.refs_to_delete.extend(self.pl.execute())

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

    def testGet(self):
        # ref = model.mock1["locationFirestoreRef"]
        ref = LocationGenericDao().insert_new(model.getLocation())
        self.to_delete.append(ref)
        location = LocationGenericDao().get(ref)
        self.assertIsNotNone(location)
        print(location.to_dict())

    def testPickupAddress(self):
        location = Location.from_pickup_address("Tenaya Hall, San Diego, CA 92161")
        d = location.to_dict()
        self.assertEqual(d, {
            'locationCategory': "user",
            'coordinates': {'latitude': 32.8794203, 'longitude': -117.2428555},
            'address': 'Tenaya Hall, San Diego, CA 92161',
        })

    def testGetUserLocation(self):
        location = Location.from_pickup_address("Tenaya Hall, San Diego, CA 92161")
        ref = LocationGenericDao().insert_new(location)
        self.to_delete.append(ref)
        location = LocationGenericDao().get(ref)
        d = location.to_dict()
        self.assertEqual(d, {
            'locationCategory': "user",
            'coordinates': {'latitude': 32.8794203, 'longitude': -117.2428555},
            'address': 'Tenaya Hall, San Diego, CA 92161',
        })
