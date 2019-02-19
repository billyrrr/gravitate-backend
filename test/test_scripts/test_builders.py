import unittest

from gravitate.scripts.location.populate_locations import buildLaxTerminal
from gravitate.scripts.event.populate_airport_events import generate_airport_events
from gravitate.scripts.utils import generateStartDatetime, generateTimestamps
from gravitate.domain.event.builders import SampleLaxEventBuilder

from test import scripts as setup_scripts


class TestBuildLaxTerminal(unittest.TestCase):

    def testBuildTerminal1(self):
        buildLaxTerminal("1")


sampleLaxEventDict = {
    "eventCategory": "airport",
    "participants": [
    ],
    "eventLocation": "LAX",
    # "locationRef": [],
    "startTimestamp": 1545033600,
    "endTimestamp": 1545119999,
    "pricing": 100
}


class TestBuildLaxEvent(unittest.TestCase):

    def setUp(self):
        self.c = setup_scripts.SetUpTestDatabase()
        self.c.clear_before()
        self.c.generate_test_data()

    def testBuildLaxSampleEvent(self):
        laxSampleEvent = SampleLaxEventBuilder(1545033600, 1545119999)
        laxSampleEventDict = laxSampleEvent.to_dict()
        self.assertDictContainsSubset(sampleLaxEventDict, laxSampleEventDict)
        self.assertIn('locationRef', laxSampleEventDict.keys(), "Dict contains locationRef as key")

    def testGenerateStartDatetime(self):
        startDatetime = generateStartDatetime("2018-12-17T11:00:00.000")
        self.assertEqual(startDatetime.timestamp(), 1545033600.0)
        self.assertEqual(startDatetime.isoformat(), "2018-12-17T00:00:00-08:00")

    def testGenerateTimestamps(self):
        startDatetime = generateStartDatetime("2018-12-17T08:00:00.000")
        timestampTupleList = generateTimestamps(startDatetime, 2)
        expectedValue = [[1545033600.0, 1545119999.0], [1545120000.0, 1545206399.0]]
        count = 0
        for startTimestamp, endTimestamp in timestampTupleList:
            self.assertEqual(startTimestamp, expectedValue[count][0])
            self.assertEqual(endTimestamp, expectedValue[count][1])
            count += 1

    def tearDown(self):
        self.c.clear_after()


class TestGenerateEvent(unittest.TestCase):

    def setUp(self):
        self.c = setup_scripts.SetUpTestDatabase()
        self.c.clear_before()
        self.c.generate_test_data()

    def testGenerateEvent(self):
        startDatetime = generateStartDatetime("2018-12-01T08:00:00.000")
        timestampTupleList = generateTimestamps(startDatetime, 2)
        eventList = generate_airport_events(timestampTupleList)
        expectedDay2EventDict = {'eventCategory': 'airport', 'participants': [], 'eventLocation': 'LAX',
                                 'startTimestamp': 1543737600, 'endTimestamp': 1543823999, 'pricing': 100,
                                 'isClosed': False}
        self.assertDictContainsSubset(expectedDay2EventDict, eventList[1].to_dict())

    def tearDown(self):
        self.c.clear_after()
