from unittest import TestCase
from gravitate.domain.event.builders_new import AirportEventBuilder
from gravitate.domain.event.models import AirportEvent
from gravitate.scripts.utils import generateStartDatetime, generateTimestamps
from gravitate.domain.event.builders import SampleLaxEventBuilder
from test import scripts


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

        self.assertEqual(b._event_dict["locationRef"].id, "testlocationid1")

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
        self.assertEqual(ae.to_dict()["locationRef"].id, "testlocationid1")
        self.assertDictContainsSubset(expected_subset, ae.to_dict())

