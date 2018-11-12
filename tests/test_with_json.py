import json
from models.ride_request import RideRequest, AirportRideRequest
import unittest

class JSONRideRequestTest(unittest.TestCase):

    def setUp(self):
        JSON_FILENAME = 'rideRequest_1.json'
        with open('tests/jsons_written_by_david_a/{}'.format(JSON_FILENAME)) as json_file:
            data = json.load(json_file)
            rideRequestDict = data['rideRequest']
            rideRequestRef = data['rideRequestRef']
            airportRideRequest: AirportRideRequest = RideRequest.fromDictAndReference(rideRequestDict, rideRequestRef)
            print(airportRideRequest.to_dict())

    def testNothing(self):
        print('nothing')