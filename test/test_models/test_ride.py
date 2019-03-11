import unittest

from gravitate.domain.rides.models import Ride, AirportRide
from gravitate import context
from .. import store

db = context.Context.db


class RideRequestTest(unittest.TestCase):
    """
    Tests that RideRequest model works.
    """

    def setUp(self):
        self.db = context.Context.db
        self.ride_request_data_2 = store.getMockRide(returnDict=True)
        self.ride_request_data_3 = store.getMockRide(returnDict=True, returnSubset=False, useDocumentRef=True)

    def testAfterDictEqualsOriginalDict2(self):
        """ Tests that to_dict returns the same dict as the passed to from_dict.

        :return:
        """
        print(self.ride_request_data_2)
        ride_request_dict = self.ride_request_data_2
        ride_request_ref = db.collection("rides").document("testrideid1")
        airport_ride_request: AirportRide = Ride.from_dict_and_reference(ride_request_dict,
                                                                                       ride_request_ref)
        result = airport_ride_request.to_dict()
        self.assertDictEqual(ride_request_dict, result,
                             "The dictionaries should equal if Ride was not modified. ")

    def testDriverRide(self):
        ride_request_dict = store.getMockRide(returnDict=True, driverStatus=True)
        ride_request_ref = db.collection("rides").document("testrideid1")
        airport_ride_request: AirportRide = Ride.from_dict_and_reference(ride_request_dict,
                                                                         ride_request_ref)
        result = airport_ride_request.to_dict()
        self.assertDictEqual(ride_request_dict, result,
                             "The dictionaries should equal if Ride was not modified. ")
