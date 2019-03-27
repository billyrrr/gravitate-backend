from unittest import TestCase, skip

from gravitate.domain.driver_navigation.builders import DriverNavigationBuilder
from gravitate.models import Orbit
from test import store


@skip("Not implemented")
class DriverNavigationModelTest(TestCase):

    def test_from_dict(self):
        d = {
            "points": [
                {
                    "type": "pickup",
                    "uid": "testuserid1",
                    "address": "testpickupaddress1",
                    "isPickedUp": False
                },
                {
                    "type": "eventDestination",
                    "uid": "testuserid1",
                    "address": "testpickupaddress1",
                    "isPickedUp": False
                }
            ],
        }
        raise NotImplementedError


@skip("Not implemented")
class DriverNavigationBuilderTest(TestCase):

    def setUp(self):
        """
        orbitDict = {
            "orbitCategory": "airportRide",
            "eventRef": mock1["eventRef"],
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
        :return:
        """
        self.orbit = Orbit.from_dict(store.getOrbitDict())

    def test_build_one_waypoint(self):
        """
        Tests that the function build_driver_navigation_from_orbit builds a driver navigation of one way-point
            and one destination.
        :return:
        """
        dict_expected = {
            "points": [
                {
                    "type": "pickup",
                    "uid": "testuserid1",
                    "address": "testpickupaddress1",
                    "isPickedUp": False
                },
                {
                    "type": "eventDestination",
                    "uid": "testuserid1",
                    "address": "testpickupaddress1",
                    "isPickedUp": False
                }
            ],
        }
        # Note that we are expecting a dict rather than DriverNavigation Object for now
        self.assertEqual(DriverNavigationBuilder.build_from_orbit(self.orbit), dict_expected)
