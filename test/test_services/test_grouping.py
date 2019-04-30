import json
from unittest import TestCase

from gravitate import main as main
from test import scripts
from test.test_main import getMockAuthHeaders
from test.test_services.utils import _create_ride_requests_for_tests


class DeleteMatchErrorTest(TestCase):

    ride_request_ids_to_delete = list()

    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()
        self.userIds = ["testuid1", "testuid2"]
        self.rideRequestIds = list()
        self.c = scripts.SetUpTestDatabase()
        self.c.clear_before()
        self.c.generate_test_data(start_string="2018-12-17T08:00:00.000", num_days=5)
        _create_ride_requests_for_tests(self.app, self.userIds, self.ride_request_ids_to_delete, self.rideRequestIds)

    def test_delete_match_invalid(self):
        """ Delete match on a ride request that is not matched to an orbit should return 400

        :return:
        """
        for uid, rid in self.ride_request_ids_to_delete:
            r = self.app.post(path='/rideRequests/' + rid + '/' + 'unmatch',
                              headers=getMockAuthHeaders(uid=uid)
                              )
            error_return_expected = {
                "message": "Trying to un-match a ride request that is not matched to an orbit yet. ",
                "status": 400
            }
            error_message_expected = error_return_expected["message"]
            error_status_code_expected = error_return_expected["status"]
            self.assertEqual(r.status_code, error_status_code_expected)
            self.assertEqual(r.json["message"], error_message_expected)

    def _tear_down(self):
        """
        Un-match all rideRequests created by the test
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
        super().tearDown()


class DeleteMatchTest(TestCase):
    ride_request_ids_to_delete = list()

    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()
        self.userIds = ["testuid1", "testuid2"]
        self.rideRequestIds = list()
        self.c = scripts.SetUpTestDatabase()
        self.c.clear_before()
        self.c.generate_test_data(start_string="2018-12-17T08:00:00.000", num_days=5)
        _create_ride_requests_for_tests(self.app, self.userIds, self.ride_request_ids_to_delete, self.rideRequestIds)
        r = self.app.post(path='/devForceMatch',
                          json=json.dumps({"rideRequestIds": self.rideRequestIds,
                                           "operationMode": "two"
                                           }
                                          ))
        print(r.data)
        self.assertEqual(r.status_code, 200)

    def test_delete_match(self):
        for uid, rid in self.ride_request_ids_to_delete:
            r = self.app.post(path='/rideRequests/'+rid+'/'+'unmatch',
                              headers=getMockAuthHeaders(uid=uid)
                              )
            self.assertEqual(r.status_code, 200)

    def _tear_down(self):
        """
        Un-match all rideRequests created by the test
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
        super().tearDown()


class GroupRequestsTest(TestCase):
    ride_request_ids_to_delete = list()

    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()
        self.userIds = ["testuid1", "testuid2"]
        self.rideRequestIds = list()
        self.c = scripts.SetUpTestDatabase()
        self.c.clear_before()
        self.c.generate_test_data(start_string="2018-12-17T08:00:00.000", num_days=5)
        _create_ride_requests_for_tests(self.app, self.userIds, self.ride_request_ids_to_delete, self.rideRequestIds)

    def testGroupRideRequestsTemp(self):
        """
        TODO move
        :return:
        """
        r = self.app.post(path='/devForceMatch',
                          json=json.dumps({"operationMode": "all"})
                          )
        print(r.data)
        self.assertEqual(r.status_code, 200)

    def testForceMatchRideRequests(self):
        r = self.app.post(path='/devForceMatch',
                          json=json.dumps({"rideRequestIds": self.rideRequestIds,
                                           "operationMode": "two"
                                           }
                                          ))
        print(r.data)
        self.assertEqual(r.status_code, 200)

    def _tear_down(self):
        """
        Un-match all rideRequests created by the test
        Deletes all rideRequests created by the test
        :return:
        """
        for uid, rid in self.ride_request_ids_to_delete:
            r = self.app.post(path='/rideRequests/'+rid+'/'+'unmatch',
                              headers=getMockAuthHeaders(uid=uid)
                              )
            print(r.json)
            assert r.status_code == 200

        for uid, rid in self.ride_request_ids_to_delete:
            r = self.app.delete(path='/rideRequests' + '/' + rid,
                                headers=getMockAuthHeaders(uid=uid)
                                )
            assert r.status_code == 200

        self.ride_request_ids_to_delete.clear()

    def tearDown(self):
        self._tear_down()
        self.c.clear_after()
        super().tearDown()
