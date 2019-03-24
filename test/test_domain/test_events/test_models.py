import unittest

from gravitate.domain.event.models import SocialEvent, AirportEvent
from gravitate import context

db = context.Context.db


class EventModelTest(unittest.TestCase):

    maxDiff = None

    def testEventFactory(self):
        eventDict = {
            "eventCategory": "airport",
            "airportCode": "LAX",
            "isClosed": False,
            "targets": [
                {
                    'eventCategory': 'airport',
                    'toEvent': True,
                    'arriveAtEventTime': {'earliest': 1545033600, 'latest': 1545119999}
                },
                {
                    'eventCategory': 'airport',
                    'toEvent': False,
                    'leaveEventTime': {'earliest': 1545033600, 'latest': 1545119999}
                }
            ],
            "localDateString": "2018-12-17",
            "pricing": 123456789,
            "parkingInfo": {
                "parkingAvailable": False,
                "parkingPrice": 0,
                "parkingLocation": "none"
            },
            "description": "what the event is",
            "name": "name of the event",
            "locationRef": "/locations/testlocationid1",
            "participants": []
        }
        event = AirportEvent.from_dict(eventDict)
        # Assert that event converts to the same dict that generated the event
        self.assertDictEqual(event.to_dict(), eventDict)

