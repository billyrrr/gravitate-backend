import unittest

from google.cloud import firestore

from gravitate.data_access import EventDao
from gravitate.models import Event
from test.factory import eventDict


class EventDAOTest(unittest.TestCase):

	def setUp(self):
		self.event = Event.fromDict(eventDict)

	def testCreate(self):
		eventRef: firestore.DocumentReference = EventDao().create(self.event)
		self.event.setFirestoreRef(eventRef)
		print("eventRef = {}".format(eventRef))

	# def testDelete(self):
	# 	eventRef: firestore.DocumentReference = EventDao().create(self.event)
	# 	self.event.setFirestoreRef(eventRef)
	# 	self.delete(eventRef)
	# 	# self.assertEquals()

	def testFindByTimestamp(self):
		event: Event = EventDao().findByTimestamp(1546504400)
		# self.assertNotEqual(None, eventRef)
		# self.assertEquals(event.startTimestamp, 1546502400)
		# self.assertEquals("BxPBnrl6kItoNc6x0NqO", event.getFirestoreRef().id)