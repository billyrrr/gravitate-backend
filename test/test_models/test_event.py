import unittest
from gravitate.models import Event, SocialEvent
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


class SocialEventModelTest(unittest.TestCase):

    def testEventFactory(self):
        d = {
            "eventCategory": "social",
            "participants": [
            ],
            "eventLocation": "Las Vegas Convention Center",
            "startTimestamp": 1545033600,
            "endTimestamp": 1545119999,
            "pricing": 100,
            "isClosed": False,
            "parkingInfo": {
                "parkingAvailable": False, "parkingPrice": 0, "parkingLocation": "none"
            },
            "description": "what the event is",
            "name": "name of the event",
            "locationRef": "/locations/testlocationid1"
        }
        eventDict = d
        event = SocialEvent.from_dict(eventDict)
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


