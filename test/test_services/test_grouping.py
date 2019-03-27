import json
from unittest import TestCase

from gravitate import main as main
from test.test_main import getMockAuthHeaders
from test.test_services.utils import _create_ride_requests_for_tests


class DeleteMatchTest(TestCase):
    ride_request_ids_to_delete = list()

    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()
        self.userIds = ["testuid1", "testuid2"]
        self.rideRequestIds = list()
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
        super().tearDown()


class GroupRequestsTest(TestCase):
    ride_request_ids_to_delete = list()

    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()
        self.userIds = ["testuid1", "testuid2"]
        self.rideRequestIds = list()
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
            assert r.status_code == 200

        for uid, rid in self.ride_request_ids_to_delete:
            r = self.app.delete(path='/rideRequests' + '/' + rid,
                                headers=getMockAuthHeaders(uid=uid)
                                )
            assert r.status_code == 200

        self.ride_request_ids_to_delete.clear()

    def tearDown(self):
        self._tear_down()
        super().tearDown()