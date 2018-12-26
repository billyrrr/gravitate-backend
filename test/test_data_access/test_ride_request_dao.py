import unittest
import json
from test import context
db = context.Context.db

from gravitate.data_access import RideRequestGenericDao
from gravitate.models import RideRequest

class RideRequestDaoTest(unittest.TestCase):

    def setUp(self):
        self.db = context.Context.db

        JSON_FILENAME = 'rideRequest_1.json'
        with open('jsons_written_by_david_a/{}'.format(JSON_FILENAME)) as json_file:
            self.rideRequestData1 = json.load(json_file)

    def testCreate(self):
        rideRequestDict = self.rideRequestData1['rideRequest']
        rideRequest = RideRequest.from_dict(rideRequestDict)
        RideRequestGenericDao().create(rideRequest)
        resultDict = rideRequest.to_dict()
        self.assertEqual(rideRequestDict, resultDict)

    # def testGet(self):
    #     rideRequestRef = self.db.collection('rideRequests').document('jhqdAdAhevewgMc7KLO1')
    #     rideRequest = RideRequestGenericDao().getRideRequest(rideRequestRef)
