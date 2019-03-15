import unittest

import gravitate.domain.request_ride.utils as controller_utils


class UtilsTest(unittest.TestCase):

    def testFindLocation(self):
        pass

    # TODO write test for findLocation
    def testFindEvent(self):
        pass

    # TODO write test for find_event
    # self.assertEqual(not None, find_event())

    def testAsTimestamp(self):
        flightLocalTimeStr = "2018-12-20T12:00:00.000"
        timestamp = controller_utils.local_time_as_timestamp(flightLocalTimeStr)
        self.assertEqual(timestamp, 1545336000.0)

    def testAsDateStr(self):
        localTimeTemplate = "2018-12-20T{}:00:00.000"
        hours = ["00", "01", "02", "12", "13", "14", "15", "22", "23"]

        for hour in hours:
            flightLocalTimeStr = localTimeTemplate.format(hour)
            dateStr = controller_utils.local_time_as_date_str(flightLocalTimeStr)
            self.assertEqual(dateStr, "2018-12-20")
