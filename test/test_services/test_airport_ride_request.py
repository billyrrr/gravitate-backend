import json
from unittest import TestCase

import gravitate.api_server.ride_request.deprecated_utils
from gravitate import main as main

import gravitate.domain.request_ride.builders as service_utils

from test.store import FormDictFactory
from test.test_main import getMockAuthHeaders
from test import scripts
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


class CreateRideRequestServiceUtilsTest(TestCase):
    maxDiff = 2000

    def testRideRequestDictBuilder(self):
        mockForm = FormDictFactory().create(hasEarliestLatest=False, returnDict=False)
        userId = 'testuserid1'
        result, _ = gravitate.api_server.ride_request.deprecated_utils.fill_ride_request_dict_builder_regression(mockForm, userId)
        valueExpected, _ = gravitate.api_server.ride_request.deprecated_utils.fill_ride_request_dict_with_form(mockForm, userId)
        self.assertDictEqual(valueExpected, result)
        self.assertIsNotNone(result["eventRef"])
        self.assertIsNotNone(result["airportLocation"])


class ReturnErrorsTest(TestCase):
    ride_request_ids_to_unmatch = list()
    ride_request_ids_to_delete = list()

    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()
        self.userIds = ["testuid1", "testuid2"]

    def testRaiseRequestAlreadyExistsError(self):
        # Create new rideRequests
        for userId in self.userIds:
            form = FormDictFactory().create(returnDict=True)
            form["flightLocalTime"] = "2018-12-20T12:00:00.000"
            form["testUserId"] = userId
            r = self.app.post(  # TODO: change everywhere to json=form (used to be json=json.dumps(form))
                path='/airportRideRequests', json=form, headers=getMockAuthHeaders(userId))
            print(r.json)
            # self.assertRaises(service_errors.RequestAlreadyExistsError)
            # self.assertIn("firestoreRef", r.json.keys())
            firestore_ref = r.json["firestoreRef"]  # Not that it is actually rideRequestId
            self.ride_request_ids_to_delete.append((userId, firestore_ref))

        userId = self.userIds[0]
        r = self.app.post(  # TODO: change everywhere to json=form (used to be json=json.dumps(form))
            path='/airportRideRequests', json=form, headers=getMockAuthHeaders(userId))
        print(r.json)
        error_return_expected = {
                "message": "Ride request on the same day (or for the same event) already exists",
                "status": 400
            }
        error_message_expected = error_return_expected["message"]
        error_status_code_expected = error_return_expected["status"]
        self.assertEqual(r.json["message"], error_message_expected)
        self.assertEqual(r.status_code, error_status_code_expected)

    def testDeleteReturnsRequestAlreadyMatchedError(self):
        """
        Test that trying to delete ride request that is already matched would return an error
        :return:
        """
        for userId in self.userIds:
            form = FormDictFactory().create(returnDict=True)
            form["flightLocalTime"] = "2018-12-20T12:00:00.000"
            form["testUserId"] = userId
            r = self.app.post(  # TODO: change everywhere to json=form (used to be json=json.dumps(form))
                path='/airportRideRequests', json=form, headers=getMockAuthHeaders(userId))
            print(r.json)
            # self.assertRaises(service_errors.RequestAlreadyExistsError)
            firestore_ref = r.json["firestoreRef"]  # Not that it is actually rideRequestId
            self.ride_request_ids_to_unmatch.append((userId, firestore_ref))
            self.ride_request_ids_to_delete.append((userId, firestore_ref))

        uid, rid = self.ride_request_ids_to_delete[0]

        r = self.app.post(path='/devForceMatch',
                          json=json.dumps({"operationMode": "two",
                                           "rideRequestIds": [i[1] for i in self.ride_request_ids_to_delete]
                                           })
                          )
        r = self.app.delete(path='/rideRequests' + '/' + rid,
                            headers=getMockAuthHeaders(uid=uid)
                            )
        error_return_expected = {
            "message": "Ride request has requestCompletion as True. Un-match from an orbit first. ",
            "status": 500
        }
        error_message_expected = error_return_expected["message"]
        error_status_code_expected = error_return_expected["status"]
        self.assertEqual(r.json["message"], error_message_expected)
        self.assertEqual(r.status_code, error_status_code_expected)

    # def testNothing(self):
    #     """
    #     Remedy for malfunctioning _tear_down. Running this test would trigger _tear_down again
    #         if you replace values in ride_request_ids_to_unmatch and ride_request_ids_to_delete.
    #     :return:
    #     """
    #     self.ride_request_ids_to_unmatch = [("testuid1", "Hwn3d0cSKMqZmv71N8YLPtdayNeA0ST1"),
    #                                        ("testuid2", "Oh5Fhhq5uEt7H95sRUmQibtIYAhCVW4v")]
    # self.ride_request_ids_to_delete = [("testuid1", "w4eCnewSikFsoE6kuVSnxgOZw9SOht89"),
    #                                    ("testuid2", "FKpHz1by9VPB6t15XqLfGt1VLfwvwLzF")]

    def _tear_down(self):
        """
        Deletes all rideRequests created by the test
        :return:
        """
        for uid, rid in self.ride_request_ids_to_unmatch:
            r = self.app.post(path='/deleteMatch',
                              json={"rideRequestId": rid},
                              headers=getMockAuthHeaders(uid=uid))
            assert r.status_code == 200

        for uid, rid in self.ride_request_ids_to_delete:
            r = self.app.delete(path='/rideRequests' + '/' + rid,
                                headers=getMockAuthHeaders(uid=uid)
                                )
            assert r.status_code == 200
        self.ride_request_ids_to_unmatch.clear()
        self.ride_request_ids_to_delete.clear()

    def tearDown(self):
        self._tear_down()
        super().tearDown()


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
                path='/airportRideRequests', json=form, headers=getMockAuthHeaders(userId))
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
        self.ride_request_ids_to_delete.clear()

    def tearDown(self):
        self._tear_down()
        super().tearDown()

    def testNewRideRequestServiceTemp(self):
        form = FormDictFactory().create(returnDict=True)
        form["flightLocalTime"] = "2018-12-20T12:00:00.000"
        # form["testUserId"] = "KlRLbJCAORfbZxCm8ou1SEBJLt62"
        r = self.app.post(path='/airportRideRequests',
                          json=form,
                          headers=getMockAuthHeaders()
                          )
        rideRequestId = r.json["firestoreRef"]
        r = self.app.delete(path='/rideRequests' + '/' + rideRequestId,
                            headers=getMockAuthHeaders()
                            )
        print(r.data)
        self.assertEqual(r.status_code, 200)
