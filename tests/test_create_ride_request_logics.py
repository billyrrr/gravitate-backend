from controllers.process_ride_request import createTarget, buildAirportRideRequestWithForm
from unittest import TestCase
from models.ride_request import RideRequest, AirportRideRequest

class MockFormTargetOnly:

    def __init__(self):
        self.earliest = "2018-12-20T09:00:00.000"
        self.latest = "2018-12-20T11:00:00.000"
        self.toEvent = True


class MockForm:

    def __init__(self):
        
        
        self.earliest = "2018-12-20T09:00:00.000"
        self.latest = "2018-12-20T11:00:00.000"
        self.toEvent = True
        
        self.driverStatus = False
        self.pickupAddress = "Tenaya Hall, San Diego, CA 92161"
        self.eventRef = "/events/testeventid1"

        self.airportLocation = "/locations/testlocationid1"
        self.flightLocalTime = "2018-12-17T12:00:00.000"
        self.flightNumber = "DL89"
    
    def toDict(self):
        return vars(self)


class testCreateRideRequestLogics(TestCase):

    def testCreateAirportTarget(self):
        mockForm = MockFormTargetOnly()
        targetDict = createTarget(mockForm).toDict()
        valueExpected = {'eventCategory': 'airportRide',
                         'toEvent': True,
                         'arriveAtEventTime':
                         {'earliest': 1545325200, 'latest': 1545332400}}
        self.assertDictEqual(targetDict, valueExpected)

    def testCreateRideRequest(self):
        mockForm = MockForm()
        result = buildAirportRideRequestWithForm(mockForm)
        valueExpected = RideRequest.fromDict({

            'rideCategory': 'airportRide',
            'pickupAddress': "Tenaya Hall, San Diego, CA 92161",
            'driverStatus': False,
            'orbitRef': None,
            'target': {'eventCategory': 'airportRide',
                         'toEvent': True,
                         'arriveAtEventTime':
                         {'earliest': 1545325200, 'latest': 1545332400}},
            'eventRef': '/events/testeventid1',
            'hasCheckedIn': False,
            'pricing': 987654321,
            "baggages": dict(),
            "disabilities": dict(),
            'flightLocalTime': "2018-12-17T12:00:00.000",
            'flightNumber': "DL89",
            "airportLocation": "/locations/testairportlocationid1"

        })
        print(result.toDict())
        self.assertDictEqual(result.toDict(), valueExpected.toDict())
