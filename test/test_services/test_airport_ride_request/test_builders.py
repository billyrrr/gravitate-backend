from unittest import TestCase

import gravitate.domain.rides.builders as service_utils
from gravitate import context
from test import scripts
from test.store import FormDictFactory

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


class AirportRideRequestDictBuilderPlusTest(TestCase):
    """
    Tests input with earliest and latest time
    """
    builder: service_utils.AirportRideRequestBuilder = None

    def setUp(self):
        self.c = scripts.SetUpTestDatabase()
        self.c.clear_before()
        self.c.generate_test_data(start_string="2018-12-17T08:00:00.000", num_days=1)

    def testSetWithForm(self):
        userId = 'testuserid1'
        d = FormDictFactory().create(hasEarliestLatest=True, returnDict=True, isE5L2=False)

        b = service_utils.AirportRideRequestBuilder().set_with_form_and_user_id(d, user_id=userId)
        expected_vars = {'user_id': 'testuserid1',
                         'flight_local_time': '2018-12-17T12:00:00.000', 'flight_number': 'DL89',
                         'airport_code': 'LAX',
                         'pickup_address': 'Tenaya Hall, San Diego, CA 92161',
                         'driver_status': False,
                         'to_event': True,
                         'earliest': "2018-12-17T09:00:00.000",
                         "latest": "2018-12-17T11:00:00.000"
                         }

        # Assert that all required variables are set
        self.assertTrue(expected_vars.items() <= vars(b).items())

    def test_time_specified(self):
        def setUp(self):
            d = FormDictFactory().create(hasEarliestLatest=True, returnDict=True, isE5L2=False)
            self.user_id = 'testuserid1'
            self.builder = service_utils.AirportRideRequestBuilder().set_with_form_and_user_id(d, user_id=self.user_id)
        setUp(self)

        self.assertTrue(self.builder.earliest_latest_specified())

    def testBuild(self):
        def setUp(self):
            d = FormDictFactory().create(hasEarliestLatest=True, returnDict=True, isE5L2=False)
            self.user_id = 'testuserid1'
            self.builder = service_utils.AirportRideRequestBuilder().set_with_form_and_user_id(d, user_id=self.user_id)
        setUp(self)
        self.builder.build_airport_ride_request()
        _d_expected = {
            'rideCategory': 'airportRide',
            # 'pickupAddress': "Tenaya Hall, San Diego, CA 92161",
            'driverStatus': False,
            'orbitRef': None,
            'target': {'eventCategory': 'airportRide',
                       'toEvent': True,
                       'arriveAtEventTime':
                           {'earliest': 1545066000, 'latest': 1545073200}},
            # 'eventRef': db.document('events', 'testeventid1'),
            'userId': self.user_id,
            'hasCheckedIn': False,
            'pricing': 987654321,
            "baggages": dict(),
            "disabilities": dict(),
            'flightLocalTime': "2018-12-17T12:00:00.000",
            'flightNumber': "DL89",
            # "airportLocation": db.document("locations", "testairportlocationid1"),
            "requestCompletion": False
        }
        result = self.builder._ride_request_dict
        print(result)
        self.assertIsNotNone(result["eventRef"])
        # self.assertTrue(_d_expected.items() <= self.builder._ride_request_dict.items())
        self.assertDictContainsSubset(_d_expected, result)


class AirportRideRequestDictBuilderTest(TestCase):
    builder: service_utils.AirportRideRequestBuilder = None

    def setUp(self):
        self.c = scripts.SetUpTestDatabase()
        self.c.clear_before()
        self.c.generate_test_data(start_string="2018-12-17T08:00:00.000", num_days=1)

    def testSetWithForm(self):
        userId = 'testuserid1'
        d = FormDictFactory().create(hasEarliestLatest=False, returnDict=True)

        b = service_utils.AirportRideRequestBuilder().set_with_form_and_user_id(d, user_id=userId)
        expected_vars = {'user_id': 'testuserid1',
                         'flight_local_time': '2018-12-17T12:00:00.000', 'flight_number': 'DL89',
                         'airport_code': 'LAX',
                         'pickup_address': 'Tenaya Hall, San Diego, CA 92161',
                         'driver_status': False,
                         'to_event': True
                         }

        # Assert that all required variables are set
        self.assertTrue(expected_vars.items() <= vars(b).items())

    def testBuild(self):
        def setUp(self):
            d = FormDictFactory().create(hasEarliestLatest=False, returnDict=True)
            self.user_id = 'testuserid1'
            self.builder = service_utils.AirportRideRequestBuilder().set_with_form_and_user_id(d, user_id=self.user_id)
        setUp(self)
        self.builder.build_airport_ride_request()
        _d_expected = {
            'rideCategory': 'airportRide',
            # 'pickupAddress': "Tenaya Hall, San Diego, CA 92161",
            'driverStatus': False,
            'orbitRef': None,
            'target': {'eventCategory': 'airportRide',
                       'toEvent': True,
                       'arriveAtEventTime':
                           {'earliest': 1545058800, 'latest': 1545069600}},
            # 'eventRef': db.document('events', 'testeventid1'),
            'userId': self.user_id,
            'hasCheckedIn': False,
            'pricing': 987654321,
            "baggages": dict(),
            "disabilities": dict(),
            'flightLocalTime': "2018-12-17T12:00:00.000",
            'flightNumber': "DL89",
            # "airportLocation": db.document("locations", "testairportlocationid1"),
            "requestCompletion": False
        }
        result = self.builder._ride_request_dict
        print(result)
        self.assertIsNotNone(result["eventRef"])
        # self.assertTrue(_d_expected.items() <= self.builder._ride_request_dict.items())
        self.assertDictContainsSubset(_d_expected, result)

    def testBuildFromEvent(self):
        """
        Note that the expected return is illogical. Remove this test if necessary.
        :return:
        """
        def testBuild(self):
            def setUp(self):
                d = FormDictFactory().create(hasEarliestLatest=False, returnDict=True)
                d["toEvent"] = False
                self.user_id = 'testuserid1'
                self.builder = service_utils.AirportRideRequestBuilder().set_with_form_and_user_id(d,
                                                                                                   user_id=self.user_id)

            setUp(self)
            self.builder.build_airport_ride_request()
            _d_expected = {
                'rideCategory': 'airportRide',
                'pickupAddress': "Tenaya Hall, San Diego, CA 92161",
                'driverStatus': False,
                'orbitRef': None,
                'target': {'eventCategory': 'airportRide',
                           'toEvent': False,
                           'arriveAtEventTime':
                               {'earliest': 1545058800, 'latest': 1545069600}},
                # 'eventRef': db.document('events', 'testeventid1'),
                'userId': self.user_id,
                'hasCheckedIn': False,
                'pricing': 987654321,
                "baggages": dict(),
                "disabilities": dict(),
                'flightLocalTime': "2018-12-17T12:00:00.000",
                'flightNumber': "DL89",
                # "airportLocation": db.document("locations", "testairportlocationid1"),
                "requestCompletion": False
            }
            # self.assertTrue(_d_expected.items() <= self.builder._ride_request_dict.items())
            self.assertDictContainsSubset(_d_expected, self.builder._ride_request_dict)

    def tearDown(self):
        self.c.clear_after()
