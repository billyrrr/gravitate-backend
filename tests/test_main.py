import main
from flask.testing import FlaskClient
from flask import request, jsonify

from main import fillRideRequestDictWithForm

from controllers.utils import createTarget, createTargetWithFlightLocalTime, saveRideRequest

from forms.ride_request_creation_form import RideRequestCreationForm, RideRequestCreationValidateForm
from forms.user_creation_form import UserCreationForm, UserCreationValidateForm

from models import RideRequest, AirportRideRequest
from models import User
from requests import request

from data_access import UserDao

from google.cloud import firestore
from firebase_admin import auth
import firebase_admin

from tests.factory import FormDictFactory
from unittest import TestCase
import json
import config
import warnings



db = config.Context.db
firebaseApp = config.Context.firebaseApp

userId = 'SQytDq13q00e0N3H4agR'

cred = config.Context._cred

userDict: dict = {
    'uid': '1GFLeGxBaaUvudqh3XYbFv2sRHx2',
    'phone_number': '+17777777777',
    'membership': 'rider',
    'display_name': 'Leon Wu',
    'photo_url': 'https://www.gstatic.com/webp/gallery/1.jpg',
    'pickupAddress': 'UCSD'
}

def getAuthHeaders():
    # user = auth.get_user(uid)
    # userIdToken = user.tokens_valid_after_timestamp
    # # userIdToken = auth.create_custom_token(uid=uid, app=firebaseApp)
    # userIdTokenMock = userIdToken
    # warnings.warn("Note that userIdTokenMock is temporary and the test may fail when the token is no longer valid.")
    userIdTokenMock = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjIzNTBiNWY2NDM0Zjc2Y2NiM2IxMTlmZGQ4OGQxMzhjOWFjNTVmY2UiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vZ3Jhdml0YXRlLWU1ZDAxIiwibmFtZSI6Ikxlb24gV3UiLCJwaWN0dXJlIjoiaHR0cHM6Ly93d3cuZ3N0YXRpYy5jb20vd2VicC9nYWxsZXJ5LzEuanBnIiwiYXVkIjoiZ3Jhdml0YXRlLWU1ZDAxIiwiYXV0aF90aW1lIjoxNTQ0MDUxMzkyLCJ1c2VyX2lkIjoiRXA3V0NqWmF0YWdkMU5yNTBUb05rSXA0V1d0MiIsInN1YiI6IkVwN1dDalphdGFnZDFOcjUwVG9Oa0lwNFdXdDIiLCJpYXQiOjE1NDQwNTQ2OTMsImV4cCI6MTU0NDA1ODI5MywiZW1haWwiOiJhbHcwNjlAdWNzZC5lZHUiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwicGhvbmVfbnVtYmVyIjoiKzE3Nzc3Nzc3Nzc3IiwiZmlyZWJhc2UiOnsiaWRlbnRpdGllcyI6eyJnb29nbGUuY29tIjpbIjExNjk5NDY0Mzg1Nzk5Nzc5NDAxMyJdLCJwaG9uZSI6WyIrMTc3Nzc3Nzc3NzciXSwiZW1haWwiOlsiYWx3MDY5QHVjc2QuZWR1Il19LCJzaWduX2luX3Byb3ZpZGVyIjoiZ29vZ2xlLmNvbSJ9fQ.UOJMNnsj2waK1BXqHksPeZJnu1RyEdVSMPWKpu0ZzOYy5HJCeHByJUeF_y-bnKWAiPx5EwcT4AbrDDmDCYz1Y4U2w91xtSnfdmlDkXk1jrtt39VWVkTeNpBEKF0GQGGoPO8xHuWVO8kOmUpmUW9ScC9SwyklfNwx_hOPHwjWFkZNoGWtYPS-oRS7w65t5-ccDAml0cqCwvoLoYBSGmHyQ9pN3CFzYAkGbkHNltV_y9ayyNq6TN-ubJ4mVeI5aePip0jklGs4oiSuyr4UJpYTrSWpPySMk9Yh9GVQQev1h4bXzHw5eovfnkJCrek9aanMaxXQnyouBico3dUVsnn9mQ"
    headers= { 'Authorization': userIdTokenMock }
    return headers

class MainAppTestCase(TestCase):

    app: FlaskClient = None

    def setUp(self):

        main.app.testing = True
        self.app = main.app.test_client()
        self.originalFrontendJson = '{"flightNumber":"DL89","flightLocalTime":"2018-12-04T12:00:00.000","airportLocation":"One World Way,Los Angeles,CA,90045-5803","pickupAddress":"9500 Gilman Dr, La Jolla, CA 92093, USA","toEvent":true,"driverStatus":false}'
        self.newJson = '{"flightNumber":"DL89","flightLocalTime":"2018-12-04T12:00:00.000","airportCode":"LAX","pickupAddress":"9500 Gilman Dr, La Jolla, CA 92093, USA","toEvent":true,"driverStatus":false}'
        self.frontendFailedJson = '{"flightNumber":"DL89","flightLocalTime":"2018-12-12T12:00:00.000","airportLocation":"One World Way,Los Angeles,CA,90045-5803","pickupAddress":"Regents Rd, San Diego, CA, USA","toEvent":true,"driverStatus":false,"airportCode":"LAX"}'

    def testCreateRideRequest(self):

        r = self.app.post(
            path='/rideRequests', json=json.dumps(FormDictFactory().create(returnDict=True)), headers=getAuthHeaders())
        assert r.status_code == 200
        # assert 'Hello World' in r.data.decode('utf-8')

    def testAuth(self):

        userIdMock = "1GFLeGxBaaUvudqh3XYbFv2sRHx2"
        mockHeaders = getAuthHeaders()
        r = self.app.post(path='/endpointTest', json = json.dumps({'testAuth': True}), headers= mockHeaders )
        responseDict:dict = json.loads(r.data)
        uid = responseDict['uid']
        self.assertEqual(uid, userIdMock)

    def testCreateRideRequestFrontend(self):

        r = self.app.post(path='/rideRequests', json=self.newJson, headers=getAuthHeaders())
        assert r.status_code == 200

    def testCreateRideRequestFailedFrontend(self):

        r = self.app.post(path='/rideRequests', json=self.frontendFailedJson, headers=getAuthHeaders())
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

    # def testGroupRideRequests(self):
    #     r = self.app.post(path='/devForceMatch',
    #                       json=json.dumps({"operationMode": "all"
    #                                        }
    #                                       ))
    #     print(r.data)
    #     self.assertEqual(r.status_code, 200)

    # def testContextTest(self):
    #     r = self.app.post(path='/contextTest', json={'key1': 'val1a'})
    #     assert r.status_code == 200

    def testGetUser(self):
        path = '/users/' + userDict["uid"]
        r = self.app.get(path=path)
        # assert r.status_code == 200
        print(r.status_code)

    def testCreateUser(self):
        path = '/users/' + userDict["uid"]
        r = self.app.post(path=path, json = json.dumps(userDict))
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


class TestCreationLogicsUtils(TestCase):

    def testCreateAirportTargetWithFlightLocalTime(self):
        mockForm = FormDictFactory().create(hasEarliestLatest=False, returnDict=False)
        targetDict = createTargetWithFlightLocalTime(
            mockForm, offsetLowAbsSec=3600, offsetHighAbsSec=10800).toDict()
        valueExpected = {'eventCategory': 'airportRide',
                         'toEvent': True,
                         'arriveAtEventTime':
                         {'earliest': 1545066000, 'latest': 1545073200}}
        self.assertDictEqual(targetDict, valueExpected)

    def testSameResultDifferentCreateTargetFunc(self):
        mockFormCTWFLT = FormDictFactory().create(
            hasEarliestLatest=False, returnDict=False)
        targetDictCTWFLT = createTargetWithFlightLocalTime(
            mockFormCTWFLT, offsetLowAbsSec=7200, offsetHighAbsSec=18000).toDict()
        mockFormCT = FormDictFactory().create(
            hasEarliestLatest=True, isE5L2=True, returnDict=False)
        targetDictCT = createTarget(mockFormCT).toDict()
        self.assertDictEqual(targetDictCTWFLT, targetDictCT)


class TestCreateRideRequestLogics(TestCase):

    def setUp(self):
        self.maxDiff = None

    def testCreateAirportTarget(self):
        mockForm = MockFormTargetOnly()
        targetDict = createTarget(mockForm).toDict()
        valueExpected = {'eventCategory': 'airportRide',
                         'toEvent': True,
                         'arriveAtEventTime':
                         {'earliest': 1545066000, 'latest': 1545073200}}
        self.assertDictEqual(targetDict, valueExpected)

    # def testSaveRideRequestToDb(self):
    #     mockForm = FormDictFactory().create(hasEarliestLatest=False, returnDict=False)
    #     rideRequestDict, _ = fillRideRequestDictWithForm(mockForm, userId)
    #     result = RideRequest.fromDict(rideRequestDict)
    #     saveRideRequest(result)

    def testCreateRideRequest(self):
        mockForm = FormDictFactory().create(hasEarliestLatest=False, returnDict=False)
        result, _ = fillRideRequestDictWithForm(mockForm, userId)
        valueExpected = RideRequest.fromDict({

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

        }).toDict()
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
        r = self.app.post(path=path, json = json.dumps(userDict))
        assert r.status_code == 200
        # assert 'Hello World' in r.data.decode('utf-8')

class UserCollectionTest(TestCase):

    def setUp(self):
        self.user = UserDao().getUserById('SQytDq13q00e0N3H4agR')

    # def testAddToEventSchedule(self):
    #     transaction = db.transaction()
    #     UserDao().addToEventScheduleWithTransaction(
    #         transaction, 
    #         userRef=self.user.getFirestoreRef(), 
    #         eventRef=db.document('events', 'testeventid1'), 
    #         toEventRideRequestRef=db.document('rideRequests', 'testriderequestid1'))

class UserDAOTest(TestCase):

    def setUp(self):
        self.user = User.fromDict(userDict)

    def testCreate(self):
        userRef: firestore.DocumentReference = UserDao().createUser(self.user)
        self.user.setFirestoreRef(userRef)
        print("userRef = {}".format(userRef))

    def testGetUserId(self):
        user = UserDao().getUserById(userDict["uid"])
        self.assertEquals(userDict['display_name'], user.display_name)
        self.assertEquals(userDict['phone_number'], user.phone_number)
        self.assertEquals(userDict['uid'], user.uid)
        self.assertEquals(userDict['membership'], user.membership)
        self.assertEquals(userDict['photo_url'], user.photo_url)
        self.assertEquals(userDict['pickupAddress'], user.pickupAddress)

class FirebaseUserTest(TestCase):
    def testGetFirebaseInfo(self):
        user = auth.get_user("1GFLeGxBaaUvudqh3XYbFv2sRHx2", app=config.Context.firebaseApp)
        print(user.display_name)

    # def testDeleteUser(self):
    #     auth.delete_user("LwkGgNe7HMRpFn6v9kcYCL7HBpx1")
    # Note that the code needs to be adapted to specify app = config.Context.firebase App

    def testUpdateUser(self):
        auth.update_user("JTKWXo5HZkab9dqQbaOaqHiSNDH2",
            phone_number = "+17777777877",
            display_name = "David Nong",
            disabled = False,
            app=config.Context.firebaseApp
        )

class FirestoreUserTest(TestCase):

    def testUserCollectionExists(self):
        uid = "1GFLeGxBaaUvudqh3XYbFv2sRHx2"
        user = UserDao().getUserById(uid)
        self.assertEqual(user.uid, userDict["uid"])
        self.assertEqual(user.membership, userDict["membership"])
        self.assertEqual(user.phone_number, userDict["phone_number"])
        self.assertEqual(user.photo_url, userDict["photo_url"])
        self.assertEqual(user.display_name, userDict["display_name"])
        self.assertEqual(user.pickupAddress, userDict["pickupAddress"])

        print(json.dumps(user.toDict()))