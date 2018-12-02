import unittest
from models.orbit import Orbit
from google.cloud import firestore
import config

# class OrbitTest(unittest.TestCase):
#     def setUp(self):
#         self.db = config.Context.db

#     def testInitWithDict(self):
#         initialData = {"rideCategory": "", "rRef": 1, "driverStatus": False, "pickupAddress": "", "hasCheckedIn": False, "eventId": 1, "orbitId": 1,
#                        "target": "", "pricing": 1, "flightTime": 1, "flightNumber": 1, "airportLocation": 1, "baggages": "", "disabilities": {}, "requestCompletion": False}
#         newOrbit = Orbit.fromDict(initialData)
#         dictNewOrbit = newOrbit.toDict()
#         self.assertEquals(initialData, dictNewOrbit)
