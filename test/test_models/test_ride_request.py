import unittest
from gravitate.models import AirportRideRequest, RideRequest
from .. import store
import json
from test import context

db = context.Context.db


class RideRequestTest(unittest.TestCase):
    """
    Tests that RideRequest model works.
    """

    def setUp(self):
        self.db = context.Context.db
        self.ride_request_data_2 = store.getMockRideRequest(returnDict=True)
        self.ride_request_data_3 = store.getMockRideRequest(returnDict=True, returnSubset=False, useDocumentRef=True)

    def testAfterDictEqualsOriginalDict2(self):
        """ Tests that to_dict returns the same dict as the passed to from_dict.

        :return:
        """
        print(self.ride_request_data_2)
        ride_request_dict = self.ride_request_data_2
        ride_request_ref = db.collection("rideRequests").document("testriderequestid1")
        airport_ride_request: AirportRideRequest = RideRequest.from_dict_and_reference(ride_request_dict,
                                                                                       ride_request_ref)
        result = airport_ride_request.to_dict()
        self.assertDictEqual(ride_request_dict, result,
                             "The dictionaries should equal if RideRequest was not modified. ")

    def testDictView(self):
        """ Tests that to_dict_view returns the correct for json for view elements

        :return:
        """
        print(self.ride_request_data_3)
        ride_request_dict = {

            'rideCategory': 'airportRide',
            'pickupAddress': "Tenaya Hall, San Diego, CA 92161",
            'driverStatus': False,
            'orbitId': None,
            'target': {'eventCategory': 'airportRide',
                   'toEvent': True,
                   'arriveAtEventTime':
                       {'earliest': 1545058800, 'latest': 1545069600}},

            'userId': "testuserid1",
            'hasCheckedIn': False,
            'pricing': 987654321,
            "baggages": dict(),
            "disabilities": dict(),
            'flightLocalTime': "2018-12-17T12:00:00.000",
            'flightNumber': "DL89",
            "requestCompletion": False,
            "locationId": self.ride_request_data_3["airportLocation"].id,
            "eventId": self.ride_request_data_3["eventRef"].id

        }

        ride_request_ref = db.collection("rideRequests").document("testriderequestid1")
        airport_ride_request: AirportRideRequest = RideRequest.from_dict_and_reference(self.ride_request_data_3,
                                                                                       ride_request_ref)
        result = airport_ride_request.to_dict_view()
        self.assertDictEqual(ride_request_dict, result)
