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
        self.rideRequestData1 = store.get_json_file('rideRequest_1.json')
        self.ride_request_data_2 = store.getMockRideRequest(returnDict=True)

    def testAfterDictEqualsOriginalDict(self):
        """ Tests that to_dict returns the same dict as the passed to from_dict.

        :return:
        """
        ride_request_dict = self.rideRequestData1['rideRequest']
        ride_request_ref = self.rideRequestData1['rideRequestRef']
        airport_ride_request: AirportRideRequest = RideRequest.from_dict_and_reference(ride_request_dict,
                                                                                       ride_request_ref)
        result = airport_ride_request.to_dict()
        self.assertDictEqual(ride_request_dict, result,
                             "The dictionaries should equal if RideRequest was not modified. ")

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
