import unittest
from gravitate.models import Event
from test import context
from test.store import getEventDict

db = context.Context.db


class EventModelTest(unittest.TestCase):

    def testEventFactory(self):
        eventDict = getEventDict()
        event = Event.from_dict(eventDict)
        # Assert that event converts to the same dict that generated the event
        self.assertDictEqual(event.to_dict(), eventDict)

    def testEventView(self):
        eventDict = getEventDict(use_firestore_ref=True)
        event = Event.from_dict(eventDict)
        result = event.to_dict_view()

        dict_view_expected = {
            'eventCategory': "airport",
            'participants': [],
            'eventLocation': "LAX",
            'eventEarliestArrival': "2018-12-17T00:00:00",
            'eventLatestArrival': "2018-12-17T23:59:59",
            'pricing': 100,
            'locationId': "testairportlocationid1",
            'isClosed': False
        }

        self.assertDictEqual(result, dict_view_expected)


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


