from unittest import TestCase

from gravitate.models import Target
from test.store import FormDictFactory


class TestTarget(TestCase):

    def testCreateAirportTarget(self):
        mock_form = FormDictFactory().create(hasEarliestLatest=False, returnDict=False)
        target_dict = Target.create_with_flight_local_time(
            mock_form.flightLocalTime, mock_form.toEvent, offset_low_abs_sec=3600, offset_high_abs_sec=10800).to_dict()
        value_expected = {'eventCategory': 'airportRide',
                          'toEvent': True,
                          'arriveAtEventTime':
                              {'earliest': 1545066000, 'latest': 1545073200}}
        self.assertDictEqual(target_dict, value_expected)

    def testCreateWithFlightLocalTime(self):
        """
        local time: "2018-12-17T08:26:40.000", timestamp: 1545064000
        :return:
        """
        o_lo = 7200
        o_hi = 18000
        target_dict = Target.create_with_flight_local_time(
            "2018-12-17T08:26:40.000", True, offset_low_abs_sec=o_lo,
            offset_high_abs_sec=o_hi).to_dict()
        expected_target_dict = {'eventCategory': 'airportRide',
                                'toEvent': True,
                                'arriveAtEventTime':
                                    {'earliest': 1545064000 - o_hi, 'latest': 1545064000 - o_lo}}
        self.assertDictEqual(expected_target_dict, target_dict)

    def testDefaultParams(self):
        """
        Test that if offsets not specified, 2-hour-before and 5-hour-before are inferred.
        local time: "2018-12-17T08:26:40.000", timestamp: 1545064000
        :return:
        """
        o_lo = 7200
        o_hi = 18000
        target_dict = Target.create_with_flight_local_time(
            "2018-12-17T08:26:40.000", True,
            offset_low_abs_sec=o_lo,
            offset_high_abs_sec=o_hi).to_dict()
        expected_target_dict = Target.create_with_flight_local_time(
            "2018-12-17T08:26:40.000", True).to_dict()
        self.assertDictEqual(expected_target_dict, target_dict)

    def testGetArrivalDatetimeView(self):
        """
        Tests that target.get_earliest_arrival_view returns  "2018-12-17T09:00:00"
            if the internal representation is 1545064000
            and that target.get_latest_arrival_view returns "2018-12-17T11:00:00"
            if the internal representation is 1545073200
        :return:
        """
        target_dict = {'eventCategory': 'airportRide',
                          'toEvent': True,
                          'arriveAtEventTime':
                              {'earliest': 1545066000, 'latest': 1545073200}}
        target = Target.from_dict(target_dict)
        self.assertEqual(target.get_earliest_arrival_view(), "2018-12-17T09:00:00")
        self.assertEqual(target.get_latest_arrival_view(), "2018-12-17T11:00:00")


    def testGetDepartureDatetimeView(self):
        """
        Tests that target.get_earliest_departure_view returns  "2018-12-17T09:00:00"
            if the internal representation is 1545064000
            and that target.get_latest_departure_view returns "2018-12-17T11:00:00"
            if the internal representation is 1545073200
        :return:
        """
        target_dict = {'eventCategory': 'airportRide',
                          'toEvent': False,
                          'leaveEventTime':
                              {'earliest': 1545066000, 'latest': 1545073200}}
        target = Target.from_dict(target_dict)
        self.assertEqual(target.get_earliest_departure_view(), "2018-12-17T09:00:00")
        self.assertEqual(target.get_latest_departure_view(), "2018-12-17T11:00:00")
