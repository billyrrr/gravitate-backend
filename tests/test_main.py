import main
from flask.testing import FlaskClient
from flask import request, jsonify
from main import fillRideRequestDictWithForm
from controllers.utils import createTarget, createTargetWithFlightLocalTime, saveRideRequest
from forms.ride_request_creation_form import RideRequestCreationForm, RideRequestCreationValidateForm
from unittest import TestCase
from models.ride_request import RideRequest, AirportRideRequest
from requests import request
import json
from tests.factory import FormDictFactory

class MainAppTestCase(TestCase):

    app: FlaskClient = None

    def setUp(self):

        main.app.testing = True
        self.app = main.app.test_client()

    def testCreateRideRequest(self):
 
        r = self.app.post(path='/rideRequests', json = json.dumps(FormDictFactory().create(returnDict = True)))

        assert r.status_code == 200
        # assert 'Hello World' in r.data.decode('utf-8')

    def testContextTest(self):
        r = self.app.post(path='/contextTest', json={'key1':'val1a'})
        assert r.status_code == 200

    def testCreateUser(self):
 
        r = self.app.post(path='/users', json = json.dumps(FormDictFactory().create(returnDict = True)))

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
        formDict = FormDictFactory().create(hasEarliestLatest=False, returnDict = True)
        form:RideRequestCreationValidateForm = RideRequestCreationValidateForm(data=formDict)
        form.validate()
        self.assertDictEqual(formDict, form.data)

    def testPrintMockForm(self):
        formDict = FormDictFactory().create(hasEarliestLatest=False, returnDict = True)
        print(json.dumps(formDict))

    def testValidate(self):
        formDict = FormDictFactory().create(hasEarliestLatest=False, returnDict = True)
        form:RideRequestCreationValidateForm = RideRequestCreationValidateForm(data=formDict)
        form.validate()
        self.assertEqual(form.validate(), True)

class TestCreationLogicsUtils(TestCase):

    def testCreateAirportTargetWithFlightLocalTime(self):
        mockForm = FormDictFactory().create(hasEarliestLatest = False, returnDict = False)
        targetDict = createTargetWithFlightLocalTime(mockForm, offsetLowAbsSec=3600, offsetHighAbsSec=10800).toDict()
        valueExpected = {'eventCategory': 'airportRide',
                         'toEvent': True,
                         'arriveAtEventTime':
                         {'earliest': 1545066000, 'latest': 1545073200}}
        self.assertDictEqual(targetDict, valueExpected)

    def testSameResultDifferentCreateTargetFunc(self):
        mockFormCTWFLT = FormDictFactory().create(hasEarliestLatest = False, returnDict = False)
        targetDictCTWFLT = createTargetWithFlightLocalTime(mockFormCTWFLT, offsetLowAbsSec=7200, offsetHighAbsSec=18000).toDict()
        mockFormCT = FormDictFactory().create(hasEarliestLatest = True, isE5L2=True, returnDict = False)
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

    def testSaveRideRequestToDb(self):
        mockForm = FormDictFactory().create(hasEarliestLatest = False, returnDict = False)
        result = RideRequest.fromDict(fillRideRequestDictWithForm(mockForm))
        saveRideRequest(result)

    def testCreateRideRequest(self):
        mockForm = FormDictFactory().create(hasEarliestLatest = False, returnDict = False)
        result = fillRideRequestDictWithForm(mockForm)
        valueExpected = RideRequest.fromDict({

            'rideCategory': 'airportRide',
            'pickupAddress': "Tenaya Hall, San Diego, CA 92161",
            'driverStatus': False,
            'orbitRef': None,
            'target': {'eventCategory': 'airportRide',
                         'toEvent': True,
                         'arriveAtEventTime':
                         {'earliest': 1545058800, 'latest': 1545069600}},
            'eventRef': '/events/testeventid1',
            'hasCheckedIn': False,
            'pricing': 987654321,
            "baggages": dict(),
            "disabilities": dict(),
            'flightLocalTime': "2018-12-17T12:00:00.000",
            'flightNumber': "DL89",
            "airportLocation": "/locations/testairportlocationid1"

        })
        self.assertDictEqual(result, valueExpected.toDict())
