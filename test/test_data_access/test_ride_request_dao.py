import unittest
import json
from test import context
db = context.Context.db

from gravitate.data_access import RideRequestGenericDao
from gravitate.models import RideRequest
from google.cloud.firestore import DocumentReference

class RideRequestDaoTest(unittest.TestCase):

    def setUp(self):
        self.db = context.Context.db

        JSON_FILENAME = 'rideRequest_1.json'
        with open('../jsons_written_by_david_a/{}'.format(JSON_FILENAME)) as json_file:
            self.rideRequestData1 = json.load(json_file)
        self.toDelete = list()

    def testCreate(self):
        rideRequestDict = self.rideRequestData1['rideRequest']
        rideRequest = RideRequest.from_dict(rideRequestDict)
        RideRequestGenericDao().create(rideRequest)
        resultDict = rideRequest.to_dict()
        self.assertEqual(rideRequestDict, resultDict)

    def testSet(self):
        rideRequestDict = self.rideRequestData1['rideRequest']
        rideRequest = RideRequest.from_dict(rideRequestDict)
        RideRequestGenericDao().create(rideRequest)
        RideRequestGenericDao().set(rideRequest)
        ref = rideRequest.get_firestore_ref()
        print(ref)
        self.toDelete.append(ref)
        d = RideRequestGenericDao().get(ref)
        self.assertEqual(rideRequestDict, d.to_dict())

    def tearDown(self):
        for ref in self.toDelete:
            ref.delete()

    # def testGet(self):
    #     rideRequestRef = self.db.collection('rideRequests').document('jhqdAdAhevewgMc7KLO1')
    #     rideRequest = RideRequestGenericDao().getRideRequest(rideRequestRef)
