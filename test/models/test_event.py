import unittest
from gravitate.models import Event
from test import config

db = config.Context.db

eventDict = {
				"eventCategory": "airport",
				"participants": [
				],
				"eventLocation": "LAX",
				"locationRef": "locations/testlocationid1",
				"startTimestamp": 1545033600,
				"endTimestamp": 1545119999,
				"pricing": 100,
				"isClosed": False
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


