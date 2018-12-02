import unittest

from scripts.populate_locations import buildLaxTerminal
from scripts.populate_airport_events import SampleLaxEventBuilder, generateStartDatetime, generateTimestamps, generateEvents


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

    def testBuildLaxSampleEvent(self):
        laxSampleEvent = SampleLaxEventBuilder()
        laxSampleEventDict = laxSampleEvent.toDict()
        self.assertDictContainsSubset(sampleLaxEventDict, laxSampleEventDict)
        self.assertIn('locationRef', laxSampleEventDict.keys(), "Dict contains locationRef as key")

    def testGenerateStartDatetime(self):
        generateStartDatetime("2018-12-17T08:00:00.000")

    def testGenerateTimestamps(self):
        startDatetime = generateStartDatetime("2018-12-17T08:00:00.000")
        timestampTupleList = generateTimestamps(startDatetime, 2)
        for startTimestamp, endTimestamp in timestampTupleList:
            print("start: {}, end: {}".format(startTimestamp, endTimestamp))


class TestGenerateEvent(unittest.TestCase):

    def testGenerateEvent(self):
        startDatetime = generateStartDatetime("2018-12-01T08:00:00.000")
        timestampTupleList = generateTimestamps(startDatetime, 2)
        eventList = generateEvents(timestampTupleList)
        expectedDay2EventDict = {'eventCategory': 'airport', 'participants': [], 'eventLocation': 'LAX',
                             'startTimestamp': 1543737600, 'endTimestamp': 1543823999, 'pricing': 100, 'isClosed':False}
        self.assertDictContainsSubset(expectedDay2EventDict, eventList[1].toDict())
