import unittest

from google.cloud import firestore

from gravitate.data_access import EventDao
from gravitate.models import Event
from test.store import eventDict
from gravitate import context

CTX = context.Context

db = CTX.db

class EventDAOTest(unittest.TestCase):

	def setUp(self):
		self.event = Event.from_dict(eventDict)

	def testCreate(self):
		eventRef: firestore.DocumentReference = EventDao().create(self.event)
		self.event.set_firestore_ref(eventRef)
		print("eventRef = {}".format(eventRef))

	# def testDelete(self):
	# 	eventRef: firestore.DocumentReference = EventDao().create(self.event)
	# 	self.event.set_firestore_ref(eventRef)
	# 	self.delete(eventRef)
	# 	# self.assertEquals()


	def testFindByTimestamp(self):
		event: Event = EventDao().find_by_timestamp(1546504400, category="airport")
		# self.assertNotEqual(None, eventRef)
		# self.assertEquals(event.startTimestamp, 1546502400)
		# self.assertEquals("BxPBnrl6kItoNc6x0NqO", event.get_firestore_ref().id)
