import unittest
from google.cloud import firestore
from models.event import Event
from data_access.event_dao import EventDao
import config

db = config.Context.db

eventDict = {
				"eventCategory": "airport",
				"participants": [
				],
				"eventLocation": "LAX",
				"locationRefs": [],
				"startTimestamp": 1545033600,
				"endTimestamp": 1545119999,
				"pricing": 100
}

class EventModelTest(unittest.TestCase):
	
	def testEventFactory(self):
		event = Event.fromDict(eventDict)
		# Assert that event converts to the same dict that generated the event
		self.assertDictEqual(event.toDict(), eventDict)

# class EventCollectionTest(unittest.TestCase):

#     def setUp(self):
#         self.user = UserDao().getUserById('SQytDq13q00e0N3H4agR')

#     def testAddToEventSchedule(self):
#         transaction = db.transaction()
#         UserDao().addToEventScheduleWithTransaction(
#             transaction, 
#             userRef=self.user.getFirestoreRef(), 
#             eventRef='/events/testeventid1', 
#             toEventRideRequestRef='/rideRequests/testriderequestid1')

class EventDAOTest(unittest.TestCase):

	def setUp(self):
		self.event = Event.fromDict(eventDict)

	def testCreate(self):
		eventRef: firestore.DocumentReference = EventDao().create(self.event)
		self.event.setFirestoreRef(eventRef)
		print("eventRef = {}".format(eventRef))

	def testFindByTimestamp(self):
		eventRef: firestore.DocumentReference = EventDao().eventCollectionReference.document("2SFSUUsmbYbF2BvGQYgA")
		self.assertEquals(eventRef, EventDao().findByTimestamp(1545399200))
	