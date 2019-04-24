import unittest

from gravitate.domain.location import LocationGenericDao, SocialEventLocation
from gravitate.domain.event.dao import EventDao
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

    maxDiff = None
    refs_to_delete = list()

    def setUp(self):
        fb_d = {
            "name": "Coachella",
            "location": {
                "latitude": 33.679974,
                "longitude": -116.237221
            },
            "id": "20281766647"
        }
        location = SocialEventLocation.from_fb_place(fb_d)
        self.location_ref = LocationGenericDao().insert_new(location)

        self.refs_to_delete.append(self.location_ref)

    def tearDown(self):
        for ref in self.refs_to_delete:
            ref.delete()

    def testEventFactory(self):
        d = {
            "eventCategory": "social",
            "isClosed": False,
            "targets": [
                {'eventCategory': 'social', 'toEvent': True,
                 'arriveAtEventTime': {'earliest': 1555077600, 'latest': 1555088400}},
                {'eventCategory': 'social', 'toEvent': False,
                 'leaveEventTime': {'earliest': 1555318740, 'latest': 1555329540}},
            ],
            "localDateString": "2019-04-12",
            "pricing": 123456789,
            "parkingInfo": None,
            "description": "Advance Sale begins Friday, 6/1 at 11AM PDT\nwww.coachella.com",
            "name": "Coachella Valley Music and Arts Festival 2019 - Weekend 1",
            "fbEventId": "137943263736990",
            "locationRef": "/locations/testlocationid1",
            "participants": []
        }

        eventDict = d
        event = SocialEvent.from_dict(eventDict)
        # Assert that event converts to the same dict that generated the event
        self.assertDictEqual(event.to_dict(), eventDict)

    def test_to_dict_view(self):
        eventDict = {
            "eventCategory": "social",
            "isClosed": False,
            "targets": [
                {'eventCategory': 'social', 'toEvent': True,
                 'arriveAtEventTime': {'earliest': 1555077600, 'latest': 1555088400}},
                {'eventCategory': 'social', 'toEvent': False,
                 'leaveEventTime': {'earliest': 1555318740, 'latest': 1555329540}},
            ],
            "localDateString": "2019-04-12",
            "pricing": 123456789,
            "parkingInfo": None,
            "description": "Advance Sale begins Friday, 6/1 at 11AM PDT\nwww.coachella.com",
            "name": "Coachella Valley Music and Arts Festival 2019 - Weekend 1",
            "fbEventId": "137943263736990",
            "locationRef": self.location_ref,
            "participants": []
        }
        event = SocialEvent.from_dict(eventDict)
        expected_view = {
            'eventCategory': "social",
            'participants': [],
            # "startLocalTime": "2019-04-12T12:00:00",
            # "endLocalTime": "2019-04-14T23:59:00",
            "localDateString": "2019-04-12",
            'earliestArrival': "2019-04-12T07:00:00",
            'earliestDeparture': "2019-04-15T01:59:00",
            'latestArrival': "2019-04-12T10:00:00",
            'latestDeparture': "2019-04-15T04:59:00",
            'pricing': 123456789,
            "description": "Advance Sale begins Friday, 6/1 at 11AM PDT\nwww.coachella.com",
            "name": "Coachella Valley Music and Arts Festival 2019 - Weekend 1",
            'locationId': self.location_ref.id,
            'address': 'Indio, CA, USA',
            'latitude': 33.679974, 'longitude': -116.237221,
            'isClosed': False,
            'parkingInfo': None,
            'fbEventId': "137943263736990"
        }

        # Assert that event converts to the same dict that generated the event
        self.assertDictEqual(event.to_dict_view(), expected_view)
