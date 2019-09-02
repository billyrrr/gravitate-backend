import time
import unittest

import test.store.model as model
from gravitate import context
from gravitate.domain.location import Location
from gravitate.domain.location.models import LocationFactory, LocationQuery
from test import scripts as setup_scripts

db = context.Context.db


class LocationDAOTest(unittest.TestCase):

    def setUp(self):
        # self.user = User.from_dict(userDict)
        self.to_delete = list()

        self.cl = setup_scripts.SetUpTestDatabase()
        self.cl.clear_before()

        self.pl = setup_scripts.scripts.populate_locations.PopulateLocationCommand()
        self.to_delete.extend(self.pl.execute())

    def tearDown(self):
        for ref in self.to_delete:
            ref.delete()

    def testFindByAirportCode(self):
        result = LocationQuery.find_by_airport_code('LAX')
        self.assertNotEqual(None, result, 'Should return a result. ')

    def testSetWithTransaction(self):
        transaction = db.transaction()
        location = model.getLocation()
        location.save(transaction=transaction)
        self.to_delete.append(location.doc_ref)
        transaction.commit()


    def testGet(self):

        l = model.getLocation()
        l.save()
        doc_id = l.doc_id
        self.to_delete.append(l.doc_ref)

        location = Location.get(doc_id=doc_id)
        self.assertIsNotNone(location)
        print(location.to_dict())

    def testPickupAddress(self):
        location = LocationFactory.from_pickup_address("Tenaya Hall, San Diego, CA 92161")
        d = location.to_dict()
        self.assertDictContainsSubset({
            'obj_type': "UserLocation",
            'coordinates': {'latitude': 32.8794203, 'longitude': -117.2428555},
            'address': 'Tenaya Hall, San Diego, CA 92161',
        }, d)

    def testGetUserLocation(self):
        location = LocationFactory.from_pickup_address("Tenaya Hall, San Diego, CA 92161")
        location.save()
        ref = location.doc_ref
        self.to_delete.append(ref)
        location = Location.get(doc_id=location.doc_id)
        d = location.to_dict()
        self.assertDictContainsSubset({
            'obj_type': "UserLocation",
            'coordinates': {'latitude': 32.8794203, 'longitude': -117.2428555},
            'address': 'Tenaya Hall, San Diego, CA 92161',
        }, d)
