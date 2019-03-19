from unittest import TestCase

from gravitate.domain.event.builders_new import AirportEventBuilder, FbEventBuilder
from gravitate.domain.event.models import AirportEvent
from test import scripts


class FbEventBuilderTest(TestCase):
    # builder: AirportEventBuilder = None

    maxDiff = None
    fbDict = {
        "description": "Advance Sale begins Friday, 6/1 at 11AM PDT\nwww.coachella.com",
        "end_time": "2019-04-14T23:59:00-0700",
        "name": "Coachella Valley Music and Arts Festival 2019 - Weekend 1",
        "place": {
            "name": "Coachella",
            "location": {
                "latitude": 33.679974,
                "longitude": -116.237221
            },
            "id": "20281766647"
        },
        "start_time": "2019-04-12T12:00:00-0700",
        "id": "137943263736990"
    }
    eventDict = {
        "airportCode": "LAX",
        "eventCategory": "airport",
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

    def setUp(self):
        self.c = scripts.SetUpTestDatabase()
        self.c.clear_before()
        self.c.generate_test_data(start_string="2018-12-17T08:00:00.000", num_days=1)

    def tearDown(self):
        self.c.clear_after()

    def testBuildDict(self):
        """
        TODO: write expected_d
        :return:
        """
        userId = 'testuserid1'
        # d = FormDictFactory().create(hasEarliestLatest=False, returnDict=True)

        b = FbEventBuilder()
        b.build_with_fb_dict(self.fbDict)

        expected_d = {
                         'description': 'Advance Sale begins Friday, 6/1 at 11AM PDT\nwww.coachella.com',
                         'name': 'Coachella Valley Music and Arts Festival 2019 - Weekend 1',
        }

        self.assertIsNotNone(b._event_dict["locationRef"].id)

        print(b._event_dict)

        # Assert that all required variables are set
        self.assertDictContainsSubset(expected_d, b._event_dict)


class EventNewBuilderTest(TestCase):
    # builder: AirportEventBuilder = None

    maxDiff = None
    eventDict = {
        "airportCode": "LAX",
        "eventCategory": "airport",
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

    def setUp(self):
        self.c = scripts.SetUpTestDatabase()
        self.c.clear_before()
        self.c.generate_test_data(start_string="2018-12-17T08:00:00.000", num_days=1)

    def tearDown(self):
        self.c.clear_after()

    def testBuildDict(self):
        """
        TODO: finish
        :return:
        """
        userId = 'testuserid1'
        # d = FormDictFactory().create(hasEarliestLatest=False, returnDict=True)

        b = AirportEventBuilder()
        b.build_airport("LAX")
        b.build_basic_info()
        b._build_target(to_event=True, start_timestamp=1545033600, end_timestamp=1545119999)
        b._build_target(to_event=False, start_timestamp=1545033600, end_timestamp=1545119999)
        b.build_descriptions("what the event is", "name of the event")
        b.build_parking()
        b._build_local_date_string("2018-12-17")

        expected_d = self.eventDict.copy()
        expected_d.pop("locationRef")

        self.assertIsNotNone(b._event_dict["locationRef"].id)

        # Assert that all required variables are set
        self.assertDictContainsSubset(expected_d, b._event_dict)

    def testBuild(self):
        b = AirportEventBuilder()
        b.build_airport("LAX")
        b.build_basic_info()
        b._build_target(to_event=True, start_timestamp=1545033600, end_timestamp=1545119999)
        b._build_target(to_event=False, start_timestamp=1545033600, end_timestamp=1545119999)
        b.build_descriptions("what the event is", "name of the event")
        b.build_parking()
        b._build_local_date_string("2018-12-17")
        ae = b.export_as_class(AirportEvent)
        self.assertIsNotNone(ae, "AirportEvent should be built")
        expected_subset = self.eventDict.copy()
        expected_subset.pop("locationRef")
        self.assertIsNotNone(ae.to_dict()["locationRef"].id)
        self.assertDictContainsSubset(expected_subset, ae.to_dict())
