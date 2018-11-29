import unittest

from scripts.populate_locations import buildLaxTerminal
from scripts.populate_airport_events import SampleLaxEventBuilder


class TestBuildLaxTerminal(unittest.TestCase):

    def testBuildTerminal1(self):
        buildLaxTerminal("1")


sampleLaxEventDict = {
    "eventCategory": "airport",
    "participants": [
    ],
    "eventLocation": "LAX",
    "locationRefs": [],
    "startTimestamp": 1545033600,
    "endTimestamp": 1545119999,
    "pricing": 100
}


class TestBuildLaxEvent(unittest.TestCase):

    def testBuildLaxSampleEvent(self):
        laxSampleEvent = SampleLaxEventBuilder()
        self.assertDictEqual(laxSampleEvent.toDict(), sampleLaxEventDict)