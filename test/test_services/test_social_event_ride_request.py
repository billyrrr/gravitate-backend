import json
from unittest import TestCase

import gravitate.services.ride_request.deprecated_utils
from gravitate import main as main

import gravitate.services.ride_request.utils as service_utils
import gravitate.services.errors as service_errors

import test.factory as factory

from test.factory import FormDictFactory
from test.test_main import getMockAuthHeaders

from test import context

db = context.Context.db


class RideRequestDictBuilderTest(TestCase):

    def testSetVariables(self):
        userId = 'testuserid1'
        d = FormDictFactory().create(hasEarliestLatest=False, returnDict=True)

        b = service_utils.RideRequestBaseBuilder().set_data(
            user_id=userId, flight_local_time=d["flightLocalTime"], flight_number=d["flightNumber"],
            # pricing=d["pricing"],  # diabilities=d["disabilities"], baggages=d["baggages"],
            airport_code=d["airportCode"], to_event=d["toEvent"], pickup_address=d["pickupAddress"],
            driver_status=d["driverStatus"]
        )
        expected_vars = {'user_id': 'testuserid1',
                         'flight_local_time': '2018-12-17T12:00:00.000', 'flight_number': 'DL89',
                         'airport_code': 'LAX',
                         'pickup_address': 'Tenaya Hall, San Diego, CA 92161',
                         'driver_status': False,
                         'to_event': True,
                         }
        # Assert that all required variables are set
        self.assertTrue(expected_vars.items() <= vars(b).items())


class SocialEventDictBuilderTest(TestCase):
    builder: service_utils.AirportRideRequestBuilder = None

    def testSetWithForm(self):
        userId = 'testuserid1'
        d = factory.EventRideRequestFormDictFactory().create()

        b = service_utils.SocialEventRideRequestBuilder().set_with_form_and_user_id(d, user_id=userId)
        expected_vars = {'user_id': 'testuserid1',
                         'event_id': "KxkUnYurkYL1hZGHdxUY",
                         'pickup_address': 'Tenaya Hall, San Diego, CA 92161',
                         'driver_status': False,
                         'to_event': True
                         }
        # Assert that all required variables are set
        self.assertTrue(expected_vars.items() <= vars(b).items())

    def testBuild(self):
        def setUp(self):
            d = factory.EventRideRequestFormDictFactory().create()
            self.user_id = 'testuserid1'
            self.builder: service_utils.SocialEventRideRequestBuilder = \
                service_utils.SocialEventRideRequestBuilder().set_with_form_and_user_id(d, user_id=self.user_id)
        setUp(self)
        self.builder.build_social_event_ride_request()
        _d_expected = {
            'rideCategory': 'eventRide',
            'pickupAddress': "Tenaya Hall, San Diego, CA 92161",
            'driverStatus': False,
            'orbitRef': None,
            'target': {'eventCategory': 'eventRide',
                       'toEvent': True,
                       'arriveAtEventTime':
                           {'earliest': 1545292800, 'latest': 1545379199}},
            # 'eventRef': db.document('events', 'testeventid1'),
            'userId': self.user_id,
            'hasCheckedIn': False,
            'pricing': 987654321,
            "baggages": dict(),
            "disabilities": dict(),

            "requestCompletion": False
        }
        # self.assertTrue(_d_expected.items() <= self.builder._ride_request_dict.items())
        self.assertDictContainsSubset(_d_expected, self.builder._ride_request_dict)


