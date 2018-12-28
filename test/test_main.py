import gravitate.main as main
from flask.testing import FlaskClient

from gravitate.services.ride_request.deprecated_utils import fill_ride_request_dict_with_form, \
    fill_ride_request_dict_builder_regression

from gravitate.controllers.utils import hasDuplicateEvent

from gravitate.forms.ride_request_creation_form import RideRequestCreationValidateForm

from gravitate.models import RideRequest, User

from gravitate.data_access import UserDao, EventDao

from google.cloud import firestore
from firebase_admin import auth

from test.factory.form import FormDictFactory
import test.factory as factory
from unittest import TestCase
import json
from test import context

db = context.Context.db
firebaseApp = context.Context.firebaseApp

userId = 'SQytDq13q00e0N3H4agR'

cred = context.Context._cred

userDict: dict = {
    'uid': 'KlRLbJCAORfbZxCm8ou1SEBJLt62',
    'phone_number': '+17777777777',
    'membership': 'rider',
    'display_name': 'Leon Wu',
    'photo_url': 'https://www.gstatic.com/webp/gallery/1.jpg',
    'pickupAddress': 'UCSD'
}


def getMockAuthHeaders(uid="testuid1"):
    # user = auth.get_user(uid)
    # userIdToken = user.tokens_valid_after_timestamp
    # # userIdToken = auth.create_custom_token(uid=uid, app=firebaseApp)
    # userIdTokenMock = userIdToken
    # warnings.warn("Note that userIdTokenMock is temporary and the test may fail when the token is no longer valid.")
    userIdTokenMock = uid  # For mocking decoding token as uid
    headers = {'Authorization': userIdTokenMock}
    return headers


class MainAppTestCase(TestCase):
    app: FlaskClient = None

    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()
        self.originalFrontendJson = '{"flightNumber":"DL89","flightLocalTime":"2018-12-04T12:00:00.000","airportLocation":"One World Way,Los Angeles,CA,90045-5803","pickupAddress":"9500 Gilman Dr, La Jolla, CA 92093, USA","toEvent":true,"driverStatus":false}'
        self.newJson = '{"flightNumber":"DL89","flightLocalTime":"2018-12-21T12:00:00.000","airportCode":"LAX","pickupAddress":"9500 Gilman Dr, La Jolla, CA 92093, USA","toEvent":true,"driverStatus":false}'
        self.frontendFailedJson = '{"flightNumber":"DL89","flightLocalTime":"2018-12-12T12:00:00.000","airportLocation":"One World Way,Los Angeles,CA,90045-5803","pickupAddress":"Regents Rd, San Diego, CA, USA","toEvent":true,"driverStatus":false,"airportCode":"LAX"}'

    def testCreateRideRequest(self):
        form = FormDictFactory().create(returnDict=True)
        form["flightLocalTime"] = "2018-12-20T12:00:00.000"
        form["testUserId"] = "KlRLbJCAORfbZxCm8ou1SEBJLt62"
        r = self.app.post(
            path='/rideRequests', json=json.dumps(form), headers=getMockAuthHeaders())
        print(r.data)
        self.fail()
        assert r.status_code == 200
        # assert 'Hello World' in r.data.decode('utf-8')

    def testCheckDuplicateEvent(self):
        # TODO: Write a test for duplicate ride request
        pass

    def testAuth(self):
        userIdMock = "1GFLeGxBaaUvudqh3XYbFv2sRHx2"
        mockHeaders = getMockAuthHeaders()
        r = self.app.post(path='/endpointTest', json=json.dumps({'testAuth': True}), headers=mockHeaders)
        responseDict: dict = json.loads(r.data)
        uid = responseDict['uid']
        self.assertEqual(uid, userIdMock)

    def testCreateRideRequestFrontend(self):
        r = self.app.post(path='/rideRequests', json=self.newJson, headers=getMockAuthHeaders())
        self.assertEqual(r.status_code, 400)

    def testCreateRideRequestFailedFrontend(self):
        r = self.app.post(path='/rideRequests', json=self.frontendFailedJson, headers=getMockAuthHeaders())
        print(r.data)
        self.assertEqual(r.status_code, 200)

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

    def testEndpointTest(self):
        postJson = {'key1': 'val1a'}
        r = self.app.post(path='/endpointTest', json=postJson, headers=getMockAuthHeaders())
        assert r.status_code == 200
        self.fail()

    def testGetUser(self):
        # path = '/users/' + userDict["uid"]
        path = '/users/Wb7tAadeIHgyVckAywkRhkPZz6L2'
        r = self.app.get(path=path)
        # assert r.status_code == 200
        print(r.status_code)

    def testCreateUser(self):
        path = '/users/' + userDict["uid"]
        r = self.app.post(path=path, json=json.dumps(userDict))
        assert r.status_code == 200
        # assert 'Hello World' in r.data.decode('utf-8')

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
        path = "/rideRequests/{}/unmatch".format(factory.mock1["rideRequestId"])
        r = self.app.post(path=path, json=requestDict, headers=getMockAuthHeaders())


class TestCreateRideRequestLogics(TestCase):

    def setUp(self):
        self.maxDiff = None

    def testHasDuplicateEvent(self):
        userId: str = "44lOjfDJoifnq1IMRdk4VKtPutF3"
        eventId: str = "8GKfUA2AbGCrgRo7n6Rt"
        eventRef: firestore.DocumentReference = EventDao().get_ref(eventId)
        result = hasDuplicateEvent(userId, eventRef)
        # Assert that hasDuplicateEvent is False since we have an entry 
        #   with equal eventRef and userId field in the database 
        self.assertNotEqual(result, False)


    # def testSaveRideRequestToDb(self):
    #     mockForm = FormDictFactory().create(hasEarliestLatest=False, returnDict=False)
    #     rideRequestDict, _ = fill_ride_request_dict_with_form(mockForm, userId)
    #     result = RideRequest.from_dict(rideRequestDict)
    #     saveRideRequest(result)

    def testFillRideRequestDict(self):
        mockForm = FormDictFactory().create(hasEarliestLatest=False, returnDict=False)
        result, _ = fill_ride_request_dict_with_form(mockForm, userId)
        valueExpected = RideRequest.from_dict({

            'rideCategory': 'airportRide',
            'pickupAddress': "Tenaya Hall, San Diego, CA 92161",
            'driverStatus': False,
            'orbitRef': None,
            'target': {'eventCategory': 'airportRide',
                       'toEvent': True,
                       'arriveAtEventTime':
                           {'earliest': 1545058800, 'latest': 1545069600}},
            'eventRef': db.document('events', 'testeventid1'),
            'userId': 'SQytDq13q00e0N3H4agR',
            'hasCheckedIn': False,
            'pricing': 987654321,
            "baggages": dict(),
            "disabilities": dict(),
            'flightLocalTime': "2018-12-17T12:00:00.000",
            'flightNumber': "DL89",
            "airportLocation": db.document("locations", "testairportlocationid1"),
            "requestCompletion": False

        }).to_dict()
        self.assertDictEqual(valueExpected, result)
        self.assertIsNotNone(result["eventRef"])
        self.assertIsNotNone(result["airportLocation"])

    def testFillRideRequestDictNew(self):
        mockForm = FormDictFactory().create(hasEarliestLatest=False, returnDict=False)
        result, _ = fill_ride_request_dict_builder_regression(mockForm, userId)
        valueExpected = RideRequest.from_dict({

            'rideCategory': 'airportRide',
            'pickupAddress': "Tenaya Hall, San Diego, CA 92161",
            'driverStatus': False,
            'orbitRef': None,
            'target': {'eventCategory': 'airportRide',
                       'toEvent': True,
                       'arriveAtEventTime':
                           {'earliest': 1545058800, 'latest': 1545069600}},
            'eventRef': db.document('events', 'testeventid1'),
            'userId': 'SQytDq13q00e0N3H4agR',
            'hasCheckedIn': False,
            'pricing': 987654321,
            "baggages": dict(),
            "disabilities": dict(),
            'flightLocalTime': "2018-12-17T12:00:00.000",
            'flightNumber': "DL89",
            "airportLocation": db.document("locations", "testairportlocationid1"),
            "requestCompletion": False

        }).to_dict()
        self.assertDictEqual(valueExpected, result)
        self.assertIsNotNone(result["eventRef"])
        self.assertIsNotNone(result["airportLocation"])


class UserEndPointTest(TestCase):
    app: FlaskClient = None

    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()

    def testGetUser(self):
        path = '/users/' + userDict["uid"]
        r = self.app.get(path=path)
        # assert r.status_code == 200
        print(r.status_code)

    def testCreateUser(self):
        path = '/users/' + userDict["uid"]
        r = self.app.post(path=path, json=json.dumps(userDict))
        assert r.status_code == 200
        # assert 'Hello World' in r.data.decode('utf-8')


class UserCollectionTest(TestCase):

    def setUp(self):
        self.user = UserDao().get_user_by_id('SQytDq13q00e0N3H4agR')

    # def testAddToEventSchedule(self):
    #     transaction = db.transaction()
    #     UserDao().add_to_event_schedule_with_transaction(
    #         transaction, 
    #         userRef=self.user.get_firestore_ref(),
    #         eventRef=db.document('events', 'testeventid1'), 
    #         toEventRideRequestRef=db.document('rideRequests', 'testriderequestid1'))


class UserDAOTest(TestCase):

    def setUp(self):
        self.user = User.from_dict(userDict)

    def testCreate(self):
        userRef: firestore.DocumentReference = UserDao().create_user(self.user)
        self.user.set_firestore_ref(userRef)
        print("userRef = {}".format(userRef))

    def testCreateTempTesting(self):
        userRef: firestore.DocumentReference = UserDao().create_user(self.user)
        self.user.set_firestore_ref(userRef)
        print("userRef = {}".format(userRef))

    def testGetUser(self):
        uid = "bUAHG6TxmENRrftWVJeGNK6qOFq2"
        user = UserDao().get_user_by_id(uid)
        print(user.to_dict())

    def testGetUserId(self):
        user = UserDao().get_user_by_id(userDict["uid"])
        self.assertEquals(userDict['display_name'], user.display_name)
        self.assertEquals(userDict['phone_number'], user.phone_number)
        self.assertEquals(userDict['uid'], user.uid)
        self.assertEquals(userDict['membership'], user.membership)
        self.assertEquals(userDict['photo_url'], user.photo_url)
        self.assertEquals(userDict['pickupAddress'], user.pickupAddress)


class FirebaseUserTest(TestCase):
    def testGetFirebaseInfo(self):
        user = auth.get_user("1GFLeGxBaaUvudqh3XYbFv2sRHx2", app=context.Context.firebaseApp)
        print(user.display_name)

    # def testDeleteUser(self):
    #     auth.delete_user("LwkGgNe7HMRpFn6v9kcYCL7HBpx1")
    # Note that the code needs to be adapted to specify app = config.Context.firebase App

    def testUpdateUser(self):
        auth.update_user("MlmgazO6xhO7c2PoTFsLy5K8v5k2",
                         phone_number="+17777777779",
                         display_name="Zixuan Rao",
                         disabled=False,
                         app=context.Context.firebaseApp
                         )


class FirestoreUserTest(TestCase):

    def testUserCollectionExists(self):
        uid = "1GFLeGxBaaUvudqh3XYbFv2sRHx2"
        user = UserDao().get_user_by_id(uid)
        self.assertEqual(user.uid, userDict["uid"])
        self.assertEqual(user.membership, userDict["membership"])
        self.assertEqual(user.phone_number, userDict["phone_number"])
        self.assertEqual(user.photo_url, userDict["photo_url"])
        self.assertEqual(user.display_name, userDict["display_name"])
        self.assertEqual(user.pickupAddress, userDict["pickupAddress"])

        print(json.dumps(user.to_dict()))


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
