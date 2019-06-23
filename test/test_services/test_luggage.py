import json
from unittest import TestCase

from gravitate import main as main
from test import scripts
from test.test_main import getMockAuthHeaders
from test.test_services.utils import _create_ride_requests_for_tests


class GetLuggageTest(TestCase):

    def setUp(self):

        self.maxDiff = None

        self.ride_request_ids_to_delete = list()

        main.app.testing = True
        self.app = main.app.test_client()
        self.userId = "testuid1"

        # Populate database with events and locations
        self.c = scripts.SetUpTestDatabase()
        self.c.clear_before()
        self.c.generate_test_data(start_string="2018-12-17T08:00:00.000", num_days=5)

        rideRequestIds = list()
        _create_ride_requests_for_tests(self.app, [self.userId], list(), rideRequestIds)
        self.rideRequestId = rideRequestIds[0]
        self.ride_request_ids_to_delete.append( (self.userId, rideRequestIds[0]) )

    def testGetEmpty(self):

        r = self.app.get(path='/rideRequests' + '/' + self.rideRequestId + '/' + "luggage",
                         headers=getMockAuthHeaders()
                         )

        dict_expected = {}

        result = dict(r.json)

        self.assertEqual(r.status_code, 200, "GET is successful")
        self.assertDictEqual(dict_expected, result)

    def testPutInvalid(self):
        to_put = {
            "luggages": [
                {
                    "luggage_type": "large",
                    "weight_in_lbs": "invalidInputInsteadOfNumber"
                },
                {
                    "luggage_type": "medium",
                    "weight_in_lbs": 15
                },
                {
                    "luggage_type": "medium",
                    "weight_in_lbs": 25
                }
            ]
        }

        print(json.dumps(to_put))

        # Note that the result may be hardcoded for now
        r = self.app.put(path='/rideRequests' + '/' + self.rideRequestId + '/' + "luggage",
                         json=to_put,
                         headers=getMockAuthHeaders()
                         )
        self.assertEqual(r.status_code, 422, "PUT luggage should fail with status 422")

    def testPutAndGet(self):

        to_put = {
            "luggages": [
                {
                    "luggage_type": "large",
                    "weight_in_lbs": 20
                },
                {
                    "luggage_type": "medium",
                    "weight_in_lbs": 15
                },
                {
                    "luggage_type": "medium",
                    "weight_in_lbs": 25
                }
            ]
        }

        print(json.dumps(to_put))

        # Note that the result may be hardcoded for now
        r = self.app.put(path='/rideRequests' + '/' + self.rideRequestId + '/' + "luggage",
                         json=to_put,
                         headers=getMockAuthHeaders()
                         )
        self.assertEqual(r.status_code, 200, "PUT luggage should be successful")

        r = self.app.get(path='/rideRequests' + '/' + self.rideRequestId + '/' + "luggage",
                         headers=getMockAuthHeaders()
                         )

        dict_expected = {
            "luggages": [
                {
                    "luggage_type": "large",
                    "weight_in_lbs": 20
                },
                {
                    "luggage_type": "medium",
                    "weight_in_lbs": 15
                },
                {
                    "luggage_type": "medium",
                    "weight_in_lbs": 25
                }
            ],
            "total_weight": 60,
            "total_count": 3
        }

        result = dict(r.json)

        self.assertEqual(r.status_code, 200, "GET luggage should be successful")
        self.assertDictEqual(dict_expected, result)

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
        super().tearDown()
