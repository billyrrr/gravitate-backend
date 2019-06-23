import json
from unittest import TestCase, skip

from gravitate import main as main
from gravitate import context
from test import scripts
from test.store import FormDictFactory
from test.test_main import getMockAuthHeaders
from test.test_services.utils import _create_ride_requests_for_tests

db = context.Context.db


class GetRequestTest(TestCase):

    ride_request_ids_to_unmatch = list()
    ride_request_ids_to_delete = list()

    def setUp(self):

        main.app.testing = True
        self.app = main.app.test_client()
        self.userIds = ["testuid1", "testuid2"]
        self.c = scripts.SetUpTestDatabase()
        self.c.clear_before()
        self.c.generate_test_data(start_string="2018-12-17T08:00:00.000", num_days=5)

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
        self.rideRequestId = rid

        r = self.app.post(path='/devForceMatch',
                          json=json.dumps({"operationMode": "two",
                                           "rideRequestIds": [i[1] for i in self.ride_request_ids_to_delete]
                                           })
                          )

    @skip("NOT IMPLEMENTED")
    def testGet(self):
        """
        NOTE: implementation in progress
        TODO: implement
        :return:
        """
        r = self.app.get(path='/rideRequests' + '/' + self.rideRequestId,
                            headers=getMockAuthHeaders()
                            )

        orbit_dict = {
            "orbitCategory": "airportRide",
            "eventRef": "testeventref1",
            "userTicketPairs": {
            },
            "chatroomRef": "testchatroomref1",
            "costEstimate": 987654321,
            "status": 1
        }

        assert r.status_code == 200
        # orbit_id = result["orbitId"]

        r = self.app.get(path='/rideRequests' + '/' + self.rideRequestId + '/orbit',
                         headers=getMockAuthHeaders()
                         )

        result = dict(r.json)

        # self.assertIsNotNone(result["locationId"])
        # self.assertIsNotNone(result["eventId"])
        # self.assertIsNone(result["orbitId"])
        # self.assertEqual(r.status_code, 200)
        self.assertDictContainsSubset(orbit_dict, result)

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

    def tearDown(self):
        self._tear_down()
        self.c.clear_after()

