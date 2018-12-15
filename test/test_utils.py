import unittest
from gravitate.models.ride_request import RideRequest, AirportRideRequest
from gravitate.data_access.event_dao import EventDao
from google.cloud import firestore
import json
from test import config

class UtilsTest(unittest.TestCase):
	
	def testFindLocation(self):
		pass
		#TODO write test for findLocation
	def testFindEvent(self):
		pass
		#TODO write test for findEvent
		#self.assertEqual(not None, findEvent())
		