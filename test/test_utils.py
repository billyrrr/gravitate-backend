import unittest
import gravitate.controllers.utils as controller_utils
import json
from test import context
import datetime
import iso8601


class UtilsTest(unittest.TestCase):

    def testFindLocation(self):
        pass

    # TODO write test for findLocation
    def testFindEvent(self):
        pass

    # TODO write test for findEvent
    # self.assertEqual(not None, findEvent())

    def testAsTimestamp(self):
        flightLocalTimeStr = "2018-12-20T12:00:00.000"
        timestamp = controller_utils._as_timestamp(flightLocalTimeStr)
        self.assertEqual(timestamp, 1545336000.0)
