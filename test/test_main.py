import gravitate.main as main
from flask.testing import FlaskClient

from gravitate.forms.ride_request_creation_form import RideRequestCreationValidateForm

from test.store.form import FormDictFactory
from test.test_users import userDict
from . import store
from unittest import TestCase
import json
from test import context

db = context.Context.db
firebaseApp = context.Context.firebaseApp

userId = 'SQytDq13q00e0N3H4agR'

cred = context.Context._cred


def getMockAuthHeaders(uid="testuid1"):
    # user = auth.get_user(uid)
    # userIdToken = user.tokens_valid_after_timestamp
    # # userIdToken = auth.create_custom_token(uid=uid, app=firebaseApp)
    # userIdTokenMock = userIdToken
    # warnings.warn("Note that userIdTokenMock is temporary and the test may fail when the token is no longer valid.")
    userIdTokenMock = uid  # For mocking decoding token as uid
    headers = {'Authorization': userIdTokenMock}
    return headers



#
# # Populate database for uc/campus location and events
# populate_locations.doWorkUc("UCSB")
# populate_airport_events.populate_events(start_string="2018-12-20T08:00:00.000", num_days=15, event_category="campus")

# Populate database for airport location and events
# class ScriptTempTestCase(TestCase):
#
#     def testNothing(self):
#         # populate_locations.doWork()
#         populate_airport_events.populate_events(start_string="2019-01-22T08:00:00.000", num_days=30)

class MainAppTestCase(TestCase):
    app: FlaskClient = None

    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()
        self.originalFrontendJson = '{"flightNumber":"DL89","flightLocalTime":"2018-12-04T12:00:00.000","airportLocation":"One World Way,Los Angeles,CA,90045-5803","pickupAddress":"9500 Gilman Dr, La Jolla, CA 92093, USA","toEvent":true,"driverStatus":false}'
        self.newJson = '{"flightNumber":"DL89","flightLocalTime":"2018-12-21T12:00:00.000","airportCode":"LAX","pickupAddress":"9500 Gilman Dr, La Jolla, CA 92093, USA","toEvent":true,"driverStatus":false}'
        self.frontendFailedJson = '{"flightNumber":"DL89","flightLocalTime":"2018-12-12T12:00:00.000","airportLocation":"One World Way,Los Angeles,CA,90045-5803","pickupAddress":"Regents Rd, San Diego, CA, USA","toEvent":true,"driverStatus":false,"airportCode":"LAX"}'

    def testCheckDuplicateEvent(self):
        # TODO: Write a test for duplicate ride request
        pass

    def testAuth(self):
        userIdMock = "1GFLeGxBaaUvudqh3XYbFv2sRHx2"
        mockHeaders = getMockAuthHeaders(uid=userIdMock)
        r = self.app.post(path='/endpointTest', json=json.dumps({'testAuth': True}), headers=mockHeaders)
        responseDict: dict = json.loads(r.data)
        uid = responseDict['uid']
        self.assertEqual(uid, userIdMock)

    # def testForceMatchRideRequests(self):
    #     r = self.app.post(path='/devForceMatch',
    #                       json=json.dumps({"rideRequestIds":
    #                                        ["0Fbk2VLNuM3ne51KbsdPFw4lF8qx3DzD",
    #                                            "0MFKquhCOtFmYDM1df69l5RasYfqPW2f"],
    #                                           "operationMode": "two"
    #                                        }
    #                                       ))
    #     print(r.data)
    #     self.assertEqual(r.status_code, 200)

    def testGroupRideRequests(self):
        r = self.app.post(path='/devForceMatch',
                          json=json.dumps({"operationMode": "all"})
                          )
        print(r.data)
        self.assertEqual(r.status_code, 200)

    # Example:
    #
    # def test_empty_db(self):
    #     rv = self.app.get('/')
    #     assert b'No entries here so far' in rv.data


class MockFormTargetOnly:

    def __init__(self):
        self.earliest = "2018-12-17T09:00:00.000"
        self.latest = "2018-12-17T11:00:00.000"
        self.toEvent = True


class TestMockFormValidation(TestCase):

    def testCreation(self):
        formDict = FormDictFactory().create(hasEarliestLatest=False, returnDict=True)
        form: RideRequestCreationValidateForm = RideRequestCreationValidateForm(
            data=formDict)
        form.validate()
        self.assertDictEqual(formDict, form.data)

    def testPrintMockForm(self):
        formDict = FormDictFactory().create(hasEarliestLatest=False, returnDict=True)
        print(json.dumps(formDict))

    def testValidate(self):
        formDict = FormDictFactory().create(hasEarliestLatest=False, returnDict=True)
        form: RideRequestCreationValidateForm = RideRequestCreationValidateForm(
            data=formDict)
        form.validate()
        self.assertEqual(form.validate(), True)


class TestEndpoints(TestCase):

    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()

    def testDeleteRideRequest(self):
        """
            Test that rideRequest is deleted and unmatched from its orbit.
        :return:
        """

        path = '/deleteRideRequest'
        requestDict = {
            "userId": "KlRLbJCAORfbZxCm8ou1SEBJLt62",
            "eventId": "CslkxeIBABOx39PXiwpT",
            "rideRequestId": "ZjOsvcOHyUKKAJwYnCSHNM0cC8YsEjWo"
        }
        r = self.app.post(path=path, json=requestDict, headers=getMockAuthHeaders())
        self.assertEqual(r.status_code, 200, "rideRequest should be safely deleted")

    def testUnmatchRideRequest(self):
        """
            Test that rideRequest is unmatched from its orbit
        :return:
        """
        requestDict = {}
        path = "/rideRequests/{}/unmatch".format(store.mock1["rideRequestId"])
        r = self.app.post(path=path, json=requestDict, headers=getMockAuthHeaders())


class DeleteRideRequestServiceTest(TestCase):
    app: FlaskClient = None

    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()
        self.newJson = '{"userId":"3NSyNVcwGhOyRyRN9f5hZonw0VQ2","eventId":"eQZMfpS0hODTGgfAn33Z","rideRequestId":"Hhbwg5oaxOkQ4fpBD9tJbPlyZxpiAaRB"}'

    def testDeleteRideRequest(self):
        r = self.app.post(
            path='/deleteRideRequest', json=self.newJson, headers=getMockAuthHeaders())
        print(r.response)
        self.assertEqual(r.status_code, 200)
