import main
from flask.testing import FlaskClient
from flask import request, jsonify
from main import fillRideRequestDictWithForm
from controllers.utils import createTarget, saveRideRequest
from forms.ride_request_creation_form import RideRequestCreationForm, RideRequestCreationValidateForm
from unittest import TestCase
from models.ride_request import RideRequest, AirportRideRequest
from requests import request
import json

class MockForm:

    def __init__(self):
        
        
        self.earliest = "2018-12-17T09:00:00.000"
        self.latest = "2018-12-17T11:00:00.000"
        self.toEvent = True
        
        self.driverStatus = False
        self.pickupAddress = "Tenaya Hall, San Diego, CA 92161"

        self.airportLocation = "LAX TBIT Terminal"
        self.flightLocalTime = "2018-12-17T12:00:00.000"
        self.flightNumber = "DL89"
    
    def toDict(self):
        return vars(self)


class MainAppTestCase(TestCase):

    app: FlaskClient = None

    def setUp(self):

        main.app.testing = True
        self.app = main.app.test_client()

    def testCreateRideRequest(self):

        r = self.app.post(path='/rideRequests', json = json.dumps(MockForm().toDict()))

        assert r.status_code == 200
        # assert 'Hello World' in r.data.decode('utf-8')

    def testContextTest(self):
        r = self.app.post(path='/contextTest', json={'key1':'val1a'})
        assert r.status_code == 200


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
        formDict = MockForm().toDict()
        form:RideRequestCreationValidateForm = RideRequestCreationValidateForm(data=formDict)
        form.validate()
        self.assertDictEqual(formDict, form.data)

    def testPrintMockForm(self):
        formDict = MockForm().toDict()
        print(json.dumps(formDict))

    def testValidate(self):
        formDict = MockForm().toDict()
        form:RideRequestCreationValidateForm = RideRequestCreationValidateForm(data=formDict)
        form.validate()
        self.assertEqual(form.validate(), True)

class TestCreateRideRequestLogics(TestCase):

    def testCreateAirportTarget(self):
        mockForm = MockFormTargetOnly()
        targetDict = createTarget(mockForm).toDict()
        valueExpected = {'eventCategory': 'airportRide',
                         'toEvent': True,
                         'arriveAtEventTime':
                         {'earliest': 1545066000, 'latest': 1545073200}}
        self.assertDictEqual(targetDict, valueExpected)

    def testSaveRideRequestToDb(self):
        mockForm = MockForm()
        result = RideRequest.fromDict(fillRideRequestDictWithForm(mockForm))
        saveRideRequest(result)

    def testCreateRideRequest(self):
        mockForm = MockForm()
        result = fillRideRequestDictWithForm(mockForm)
        valueExpected = RideRequest.fromDict({

            'rideCategory': 'airportRide',
            'pickupAddress': "Tenaya Hall, San Diego, CA 92161",
            'driverStatus': False,
            'orbitRef': None,
            'target': {'eventCategory': 'airportRide',
                         'toEvent': True,
                         'arriveAtEventTime':
                         {'earliest': 1545066000, 'latest': 1545073200}},
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
