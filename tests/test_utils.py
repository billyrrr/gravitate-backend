import unittest
from models.ride_request import RideRequest, AirportRideRequest
from data_access.event_dao import EventDao
from google.cloud import firestore
import json
import config

class UtilsTest(unittest.TestCase):
	
	def testFindLocation(self):
		pass
		#TODO write tests for findLocation
	def testFindEvent(self):
		pass
		#TODO write tests for findEvent
		#self.assertEqual(not None, findEvent())
		