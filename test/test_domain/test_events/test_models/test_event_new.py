import unittest

from gravitate.domain.event.models import SocialEvent, AirportEvent
from gravitate import context

db = context.Context.db


class EventModelTest(unittest.TestCase):

    maxDiff = None

    def testEventFactory(self):
        d = {
            "eventCategory": "airport",
            "participants": [
            ],
            "targets": [
                {
                    'eventCategory': 'airportRide',
                    'toEvent': True,
                    'arriveAtEventTime': {'earliest': 1545066000, 'latest': 1545073200}
                },
                {
                    'eventCategory': 'airportRide',
                    'toEvent': False,
                    'leaveEventTime': {'earliest': 1545066000, 'latest': 1545073200}
                }
            ],
            "airportCode": "LAX",
            "localDateString": "2018-12-17",  # YYYY-MM-DD
            "pricing": 100,
            "isClosed": False,
            "parkingInfo": {
                "parkingAvailable": False,
                "parkingPrice": 0,
                "parkingLocation": "none"
            },
            "description": "what the event is",
            "name": "name of the event",
            "locationRef": "/locations/testlocationid1"
        }
        eventDict = d
        event = AirportEvent.from_dict(eventDict)
        # Assert that event converts to the same dict that generated the event
        self.assertDictEqual(event.to_dict(), eventDict)

    # def testEventView(self):
    #     eventDict = getEventDict(use_firestore_ref=True)
    #     event = Event.from_dict(eventDict)
    #     result = event.to_dict_view()
    #
    #     dict_view_expected = {
    #         'eventCategory': "airport",
    #         'participants': [],
    #         'eventLocation': "LAX",
    #         'eventEarliestArrival': "2018-12-17T00:00:00",
    #         'eventLatestArrival': "2018-12-17T23:59:59",
    #         'pricing': 100,
    #         'locationId': "testairportlocationid1",
    #         'isClosed': False
    #     }
    #
        # self.assertDictEqual(result, dict_view_expected)


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




