import json
from unittest import TestCase
from urllib.parse import urlencode

from gravitate import main as main
from test.factory import FormDictFactory
from test.test_main import getMockAuthHeaders


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
            firestore_ref = r.json["firestoreRef"] # Not that it is actually rideRequestId
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

