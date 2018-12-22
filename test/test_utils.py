import unittest
from gravitate.models.ride_request import RideRequest, AirportRideRequest
from gravitate.data_access.event_dao import EventDao
import gravitate.controllers.utils as controller_utils
from google.cloud import firestore
import json
from test import config
import datetime
import iso8601

class UtilsTest(unittest.TestCase):
	
	def testFindLocation(self):
		pass
		#TODO write test for findLocation
	def testFindEvent(self):
		pass
		#TODO write test for findEvent
		#self.assertEqual(not None, findEvent())

	def testAsTimestamp(self):
		flightLocalTimeStr = "2018-12-20T12:00:00.000"
		# flightLocalTime = iso8601.parse_date(flightLocalTimeStr)
		timestamp = controller_utils._as_timestamp(flightLocalTimeStr)
		self.assertEqual(timestamp, 1545336000.0)