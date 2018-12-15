import unittest
from gravitate.models import Orbit

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

    def testInitWithDict(self):
        newOrbit = Orbit.fromDict(orbitDict)
        dictNewOrbit = newOrbit.toDict()
        self.assertDictEqual(orbitDict, dictNewOrbit)
