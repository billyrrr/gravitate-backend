import unittest
from gravitate.models import Event
from test import context
from test.factory import eventDict

db = context.Context.db


class EventModelTest(unittest.TestCase):

	def testEventFactory(self):
		event = Event.from_dict(eventDict)
		# Assert that event converts to the same dict that generated the event
		self.assertDictEqual(event.to_dict(), eventDict)

# class EventCollectionTest(unittest.TestCase):

#     def setUp(self):
#         self.user = UserDao().get_user_by_id('SQytDq13q00e0N3H4agR')

#     def testAddToEventSchedule(self):
#         transaction = db.transaction()
#         UserDao().add_to_event_schedule_with_transaction(
#             transaction,
#             userRef=self.user.get_firestore_ref(),
#             eventRef='/events/testeventid1',
#             toEventRideRequestRef='/rideRequests/testriderequestid1')


