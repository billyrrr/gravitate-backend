import json
import warnings
from unittest import TestCase

from gravitate import main as main
from test import scripts
from test.test_main import getMockAuthHeaders
from test.test_services.utils import _create_ride_requests_for_tests


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

    def testGroupRideRequestsNonCron(self):
        """
        Test that calling the resource from places other than cron returns a 401 unauthorized.
        :return:
        """
        r = self.app.get(path='/groupAll')
        print(r.data)
        self.assertEqual(r.status_code, 401)

    def testGroupRideRequestsAll(self):
        """
        Test that the all ride requests are queued to be grouped.
        :return:
        """
        r = self.app.get(path='/groupAll',
                         headers={
                              "X-Appengine-Cron": True
                         })
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
            if r.status_code != 200:
                warnings.warn("ride request rid: {} not unmatched".format(rid))

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