import json
from unittest import TestCase
from urllib.parse import urlencode

from gravitate import main as main

from gravitate.models import RideRequest, Target
import gravitate.services.ride_request.utils as service_utils

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


class AirportRideRequestDictBuilderTest(TestCase):
    builder: service_utils.AirportRideRequestBuilder = None

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
            'pickupAddress': "Tenaya Hall, San Diego, CA 92161",
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
        # self.assertTrue(_d_expected.items() <= self.builder._ride_request_dict.items())
        self.assertDictContainsSubset(_d_expected, self.builder._ride_request_dict)


class TestTarget(TestCase):

    def testCreateAirportTarget(self):
        mockForm = FormDictFactory().create(hasEarliestLatest=False, returnDict=False)
        targetDict = Target.create_with_flight_local_time(
            mockForm.flightLocalTime, mockForm.toEvent, offsetLowAbsSec=3600, offsetHighAbsSec=10800).to_dict()
        valueExpected = {'eventCategory': 'airportRide',
                         'toEvent': True,
                         'arriveAtEventTime':
                             {'earliest': 1545066000, 'latest': 1545073200}}
        self.assertDictEqual(targetDict, valueExpected)

    def testCreateWithFlightLocalTime(self):
        """
        local time: "2018-12-17T08:26:40.000", timestamp: 1545064000
        :return:
        """
        oLo = 7200
        oHi = 18000
        target_dict = Target.create_with_flight_local_time(
            "2018-12-17T08:26:40.000", True, offsetLowAbsSec=oLo,
            offsetHighAbsSec=oHi).to_dict()
        expected_target_dict = {'eventCategory': 'airportRide',
                          'toEvent': True,
                          'arriveAtEventTime':
                              {'earliest': 1545064000-oHi, 'latest': 1545064000-oLo}}
        self.assertDictEqual(expected_target_dict, target_dict)

    def testDefaultParams(self):
        """
        Test that if offsets not specified, 2-hour-before and 5-hour-before are inferred.
        local time: "2018-12-17T08:26:40.000", timestamp: 1545064000
        :return:
        """
        oLo = 7200
        oHi = 18000
        target_dict = Target.create_with_flight_local_time(
            "2018-12-17T08:26:40.000", True,
            offsetLowAbsSec=oLo,
            offsetHighAbsSec=oHi).to_dict()
        expected_target_dict = Target.create_with_flight_local_time(
            "2018-12-17T08:26:40.000", True).to_dict()
        self.assertDictEqual(expected_target_dict, target_dict)
    #
    # def testCreateAirportTarget(self):
    #     mockForm = FormDictFactory.create(
    #         hasEarliestLatest=False, returnDict=False)
    #     targetDict = Target.create_with_form(mockForm).to_dict()
    #     valueExpected = {'eventCategory': 'airportRide',
    #                      'toEvent': True,
    #                      'arriveAtEventTime':
    #                          {'earliest': 1545066000, 'latest': 1545073200}}
    #     self.assertDictEqual(targetDict, valueExpected)


# def testSetWithForm(self):

class CreateRideRequestServiceUtilsTest(TestCase):
    maxDiff = 2000

    def testRideRequestDictBuilder(self):
        mockForm = FormDictFactory().create(hasEarliestLatest=False, returnDict=False)
        userId = 'testuserid1'
        result, _ = service_utils.fill_ride_request_dict_builder_regression(mockForm, userId)
        valueExpected, _ = service_utils.fill_ride_request_dict_with_form(mockForm, userId)
        self.assertDictEqual(valueExpected, result)
        self.assertIsNotNone(result["eventRef"])
        self.assertIsNotNone(result["airportLocation"])


class RefactorTempTest(TestCase):
    ride_request_ids_to_delete = list()

    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()
        self.userIds = ["testuid1", "testuid2"]

    def testCreateRideRequestsTemp(self):
        # Create new rideRequests
        for userId in self.userIds:
            form = FormDictFactory().create(returnDict=True)
            form["flightLocalTime"] = "2018-12-20T12:00:00.000"
            form["testUserId"] = userId
            r = self.app.post(  # TODO: change everywhere to json=form (used to be json=json.dumps(form))
                path='/rideRequests', json=form, headers=getMockAuthHeaders(userId))
            print(r.json)
            self.assertIn("firestoreRef", r.json.keys())
            firestore_ref = r.json["firestoreRef"]  # Not that it is actually rideRequestId
            self.ride_request_ids_to_delete.append((userId, firestore_ref))

    def testGroupRideRequestsTemp(self):
        """
        TODO move
        :return:
        """
        r = self.app.post(path='/devForceMatch',
                          json=json.dumps({"operationMode": "all"})
                          )

    #
    # def testCreateRideRequestQueryString(self):
    #     """
    #     This method tests creating rideRequest with POST url querystring 
    #     Deprecated
    #     :return:
    #     """
    #     form = FormDictFactory().create(returnDict=True)
    #     form["flightLocalTime"] = "2018-12-20T12:00:00.000"
    #     # form["testUserId"] = "KlRLbJCAORfbZxCm8ou1SEBJLt62"
    #     r = self.app.post(path='/testReqParse?' + urlencode(form),
    #                       headers=getMockAuthHeaders()
    #                       )
    #     self.fail()

    def _tear_down(self):
        """
        Deletes all rideRequests created by the test
        :return:
        """
        for uid, rid in self.ride_request_ids_to_delete:
            r = self.app.delete(path='/rideRequests' + '/' + rid,
                                headers=getMockAuthHeaders(uid=uid)
                                )
            assert r.status_code == 200

    def tearDown(self):
        self._tear_down()
        super().tearDown()

    def testNewRideRequestServiceTemp(self):
        form = FormDictFactory().create(returnDict=True)
        form["flightLocalTime"] = "2018-12-20T12:00:00.000"
        # form["testUserId"] = "KlRLbJCAORfbZxCm8ou1SEBJLt62"
        r = self.app.post(path='/rideRequests',
                          json=form,
                          headers=getMockAuthHeaders()
                          )
        rideRequestId = r.json["firestoreRef"]
        r = self.app.delete(path='/rideRequests' + '/' + rideRequestId,
                            headers=getMockAuthHeaders()
                            )
        self.assertEqual(r.status_code, 200)
