import json
from unittest import TestCase

from gravitate import main as main
from gravitate import context
from test import scripts
from test.store import FormDictFactory
from test.test_main import getMockAuthHeaders
from test.test_services.utils import _create_ride_requests_for_tests

db = context.Context.db


class CreateRideRequestServiceUtilsTest(TestCase):
    maxDiff = 2000

    def setUp(self):
        self.c = scripts.SetUpTestDatabase()
        self.c.clear_before()
        self.c.generate_test_data(start_string="2018-12-17T08:00:00.000", num_days=5)

    def tearDown(self):
        self.c.clear_after()
    #
    # def testRideRequestDictBuilder(self):
    #     mockForm = FormDictFactory().create(hasEarliestLatest=False, returnDict=False)
    #     userId = 'testuserid1'
    #     result, _ = gravitate.api_server.ride_request.deprecated_utils.fill_ride_request_dict_builder_regression(mockForm, userId)
    #     valueExpected, _ = gravitate.api_server.ride_request.deprecated_utils.fill_ride_request_dict_with_form(mockForm, userId)
    #     self.assertDictEqual(valueExpected, result)
    #     self.assertIsNotNone(result["eventRef"])
    #     self.assertIsNotNone(result["airportLocation"])


class ReturnErrorsTest(TestCase):
    ride_request_ids_to_unmatch = list()
    ride_request_ids_to_delete = list()

    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()
        self.userIds = ["testuid1", "testuid2"]
        self.c = scripts.SetUpTestDatabase()
        self.c.clear_before()
        self.c.generate_test_data(start_string="2018-12-17T08:00:00.000", num_days=5)

    def tearDown(self):
        self._tear_down()
        self.c.clear_after()

    def testRaiseRequestAlreadyExistsError(self):
        # Create new rideRequests
        for userId in self.userIds:
            form = FormDictFactory().create(returnDict=True)
            form["flightLocalTime"] = "2018-12-20T12:00:00.000"
            form["testUserId"] = userId
            r = self.app.post(  # TODO: change everywhere to json=form (used to be json=json.dumps(form))
                path='/rideRequests', json=form, headers=getMockAuthHeaders(userId))
            print(r.json)
            # self.assertRaises(service_errors.RequestAlreadyExistsError)
            # self.assertIn("firestoreRef", r.json.keys())
            firestore_ref = r.json["firestoreRef"]  # Not that it is actually rideRequestId
            self.ride_request_ids_to_delete.append((userId, firestore_ref))

        userId = self.userIds[0]
        r = self.app.post(  # TODO: change everywhere to json=form (used to be json=json.dumps(form))
            path='/rideRequests', json=form, headers=getMockAuthHeaders(userId))
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
                path='/rideRequests', json=form, headers=getMockAuthHeaders(userId))
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
            r = self.app.post(path='/rideRequests/'+rid+'/'+'unmatch',
                              headers=getMockAuthHeaders(uid=uid))
            assert r.status_code == 200

        for uid, rid in self.ride_request_ids_to_delete:
            r = self.app.delete(path='/rideRequests' + '/' + rid,
                                headers=getMockAuthHeaders(uid=uid)
                                )
            assert r.status_code == 200
        self.ride_request_ids_to_unmatch.clear()
        self.ride_request_ids_to_delete.clear()


class RequestRideTest(TestCase):
    ride_request_ids_to_delete = list()

    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()
        self.userIds = ["testuid1", "testuid2"]
        self.c = scripts.SetUpTestDatabase()
        self.c.clear_before()
        self.c.generate_test_data(start_string="2018-12-17T08:00:00.000", num_days=5)

    def testCreateRideRequestsTemp(self):
        # Create new rideRequests
        for userId in self.userIds:
            form = FormDictFactory().create(returnDict=True)
            form["flightLocalTime"] = "2018-12-20T12:00:00.000"
            form["testUserId"] = userId
            r = self.app.post(  # TODO: change everywhere to json=form (used to be json=json.dumps(form))
                path='/rideRequests', json=form, headers=getMockAuthHeaders(userId))
            print(r)
            self.assertIn("firestoreRef", r.json.keys())
            firestore_ref = r.json["firestoreRef"]  # Not that it is actually rideRequestId
            self.ride_request_ids_to_delete.append((userId, firestore_ref))

    def testCreateRideRequestsEarliestLatest(self):
        # Create new rideRequests
        for userId in self.userIds:
            form = FormDictFactory().create(returnDict=True, hasEarliestLatest=True, isE5L2=False)
            form["flightLocalTime"] = "2018-12-20T12:00:00.000"
            form["testUserId"] = userId
            r = self.app.post(  # TODO: change everywhere to json=form (used to be json=json.dumps(form))
                path='/rideRequests', json=form, headers=getMockAuthHeaders(userId))
            print(r)
            self.assertIn("firestoreRef", r.json.keys())
            firestore_ref = r.json["firestoreRef"]  # Not that it is actually rideRequestId
            self.ride_request_ids_to_delete.append((userId, firestore_ref))

            r = self.app.get(path='/rideRequests' + '/' + firestore_ref,
                             headers=getMockAuthHeaders()
                             )

            result = dict(r.json)
            self.assertEqual(result["target"]["arriveAtEventTime"]["earliest"], 1545066000)

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
        self.c.clear_after()


class DeleteRequestTest(TestCase):
    ride_request_ids_to_delete = list()

    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()
        self.userId = "testuid1"

        self.c = scripts.SetUpTestDatabase()
        self.c.clear_before()
        self.c.generate_test_data(start_string="2018-12-17T08:00:00.000", num_days=5)

        rideRequestIds = list()
        _create_ride_requests_for_tests(self.app, [self.userId], list(), rideRequestIds)
        self.rideRequestId = rideRequestIds.pop()

    def tearDown(self):
        self.c.clear_after()
        self.c.clear_after()

    def testDelete(self):
        r = self.app.delete(path='/rideRequests' + '/' + self.rideRequestId,
                            headers=getMockAuthHeaders()
                            )
        print(r.data)
        self.assertEqual(r.status_code, 200)


class GetRequestTest(TestCase):

    def setUp(self):

        self.maxDiff = None

        self.ride_request_ids_to_delete = list()

        main.app.testing = True
        self.app = main.app.test_client()
        self.userId = "testuid1"

        self.c = scripts.SetUpTestDatabase()
        self.c.clear_before()
        self.c.generate_test_data(start_string="2018-12-17T08:00:00.000", num_days=5)

        rideRequestIds = list()
        _create_ride_requests_for_tests(self.app, [self.userId], list(), rideRequestIds)
        self.rideRequestId = rideRequestIds[0]
        self.ride_request_ids_to_delete.append( (self.userId, rideRequestIds[0]) )

    def testGet(self):
        r = self.app.get(path='/rideRequests' + '/' + self.rideRequestId,
                            headers=getMockAuthHeaders()
                            )

        ride_request_dict = {

            'rideCategory': 'airportRide',
            'pickupAddress': "Tenaya Hall, San Diego, CA 92161",
            'driverStatus': False,

            'target': {'eventCategory': 'airportRide',
                       'toEvent': True,
                       'arriveAtEventTime':
                           {'earliest': 1545318000, 'latest': 1545328800}},

            'userId': "testuid1",
            'hasCheckedIn': False,
            'pricing': 987654321,
            "baggages": dict(),
            "disabilities": dict(),
            'flightLocalTime': "2018-12-20T12:00:00.000",
            'flightNumber': "DL89",
            "requestCompletion": False,

        }


        result = dict(r.json)
        print(json.dumps(result))

        self.assertIsNotNone(result["locationId"])
        self.assertIsNotNone(result["eventId"])
        self.assertIsNone(result["orbitId"])
        self.assertEqual(r.status_code, 200)
        self.assertDictContainsSubset(ride_request_dict, result)

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
        self.c.clear_after()


