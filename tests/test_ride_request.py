import unittest
from models.ride_request import RideRequest
from google.cloud import firestore


class RideRequestTest(unittest.TestCase):
    def setUp(self):
        self.db = firestore.Client()

    def testInitWithDict(self):
        initialData = {"rideCategory": "", "rRef": 1, "driverStatus": False, "pickupAddress": "", "hasCheckedIn": False, "eventRef": 1, "orbitRef": 1,
                       "target": "", "pricing": 1, "flightTime": 1, "flightNumber": 1, "airportLocation": 1, "baggages": "", "disabilities": {}, "requestCompletion": False}
        newRideRequest = RideRequest.from_dict(initialData)
        dictNewRideRequest = vars(newRideRequest)
        self.assertEquals(initialData, dictNewRideRequest)
