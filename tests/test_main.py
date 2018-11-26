from main import fillRideRequestDictWithForm
from controllers.utils import createTarget
from forms.ride_request_creation_form import RideRequestCreationForm
from unittest import TestCase
from models.ride_request import RideRequest, AirportRideRequest
from requests import request

class MockFormTargetOnly:

    def __init__(self):
        self.earliest = "2018-12-17T09:00:00.000"
        self.latest = "2018-12-17T11:00:00.000"
        self.toEvent = True


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


class TestMockFormValidation(TestCase):

    def testCreation(self):
        formDict = MockForm().toDict()
        print(formDict)
        form:RideRequestCreationForm = RideRequestCreationForm(data=formDict)
        form.validate()
        self.assertDictEqual(formDict, form.data)

class TestCreateRideRequestLogics(TestCase):

    def testCreateAirportTarget(self):
        mockForm = MockFormTargetOnly()
        targetDict = createTarget(mockForm).toDict()
        valueExpected = {'eventCategory': 'airportRide',
                         'toEvent': True,
                         'arriveAtEventTime':
                         {'earliest': 1545066000, 'latest': 1545073200}}
        self.assertDictEqual(targetDict, valueExpected)

    def testCreateRideRequest(self):
        mockForm = MockForm()
        result = fillRideRequestDictWithForm(mockForm)
        print(result)
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
