import unittest
from models.ride_request import RideRequest, AirportRideRequest
from data_access.event_dao import EventDao
from google.cloud import firestore
import json

class UtilsTest(unittest.TestCase):
    def setUp(self):
        self.db = firestore.Client.from_service_account_json('gravitate-e5d01-dc7b00d7b8e3.json')

        JSON_FILENAME = 'rideRequest_1.json'
        with open('tests/jsons_written_by_david_a/{}'.format(JSON_FILENAME)) as json_file:
            self.rideRequestData1 = json.load(json_file)


    # def testFindEvent(self):
    #     self.assertEqual("refE01", findEvent(self))
        