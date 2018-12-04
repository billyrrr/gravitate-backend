import unittest
from models.orbit import Orbit
import data_access
from google.cloud import firestore
import config

orbitDict = {
	"orbitCategory": "airportRide",
	"eventRef": "testeventref1",
	"userTicketPairs": {
				"testuserid1": {
					"rideRequestRef": None,
					"userWillDrive": False,
					"hasCheckedIn": False,
					"inChat": True,
					"pickupAddress": "testpickupaddress1"
				}
	},
	"chatroomRef": "testchatroomref1",
	"costEstimate": 987654321,
	"status": 1
}


class OrbitTest(unittest.TestCase):
	def setUp(self):
		self.db = config.Context.db

	def testInitWithDict(self):
		newOrbit = Orbit.fromDict(orbitDict)
		dictNewOrbit = newOrbit.toDict()
		self.assertDictEqual(orbitDict, dictNewOrbit)

	def testCreateOrbit(self):
		newOrbit = Orbit.fromDict(orbitDict)
		orbitRef = data_access.OrbitDao().create(newOrbit)
		self.assertIsNotNone(orbitRef)
