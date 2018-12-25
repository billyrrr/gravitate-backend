import unittest
from gravitate.models import AirportRideRequest, RideRequest
import json
from test import context

db = context.Context.db


class RideRequestTest(unittest.TestCase):
    def setUp(self):
        self.db = context.Context.db

        JSON_FILENAME = 'rideRequest_1.json'
        with open('jsons_written_by_david_a/{}'.format(JSON_FILENAME)) as json_file:
            self.rideRequestData1 = json.load(json_file)

    # def testInitWithDict(self):
    #     initialData = {"rideCategory": "", "rRef": 1, "driverStatus": False, "pickupAddress": "", "hasCheckedIn": False, "eventRef": 1, "orbitRef": 1,
    #                    "target": "", "pricing": 1, "flightTime": 1, "flightNumber": 1, "airportLocation": 1, "baggages": "", "disabilities": {}, "requestCompletion": False}
    #     newRideRequest = RideRequest.from_dict(initialData)
    #     dictNewRideRequest = vars(newRideRequest)
    #     self.assertEquals(initialData, dictNewRideRequest)

    def testAfterDictEqualsOriginalDict(self):
        rideRequestDict = self.rideRequestData1['rideRequest']
        rideRequestRef = self.rideRequestData1['rideRequestRef']
        airportRideRequest: AirportRideRequest = RideRequest.from_dict_and_reference(rideRequestDict, rideRequestRef)
        afterDict = airportRideRequest.to_dict()
        self.assertDictEqual(rideRequestDict, afterDict,
                             "The dictionaries should equal if RideRequest was not modified. ")
