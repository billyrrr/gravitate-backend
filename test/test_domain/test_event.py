import unittest

from gravitate.domain.event import utils as event_utils


class EventUtilsTest(unittest.TestCase):

    def test_local_time_from_timestamp(self):
        local_time_expected = "2018-12-17T08:00:00"
        timestamp = 1545062400
        result = event_utils.local_time_from_timestamp(timestamp)
        self.assertEqual(local_time_expected, result)
