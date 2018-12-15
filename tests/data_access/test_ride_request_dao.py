import unittest
import json
from tests import config
db = config.Context.db

from data_access import RideRequestGenericDao
from models import RideRequest

class RideRequestDaoTest(unittest.TestCase):

    def setUp(self):
        self.db = config.Context.db

        JSON_FILENAME = 'rideRequest_1.json'
        with open('../jsons_written_by_david_a/{}'.format(JSON_FILENAME)) as json_file:
            self.rideRequestData1 = json.load(json_file)

    def testCreation(self):
        rideRequestDict = self.rideRequestData1['rideRequest']
        rideRequest = RideRequest.fromDict(rideRequestDict)
        documentRef = RideRequestGenericDao().create(rideRequest)
        rideRequest.setFirestoreRef(documentRef)
        print(vars(rideRequest))

    # def testGet(self):
    #     rideRequestRef = self.db.collection('rideRequests').document('jhqdAdAhevewgMc7KLO1')
    #     rideRequest = RideRequestGenericDao().getRideRequest(rideRequestRef)