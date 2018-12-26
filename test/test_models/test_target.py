from unittest import TestCase

from gravitate.models import Target
from test.factory import FormDictFactory


class TestTarget(TestCase):

    def testCreateAirportTarget(self):
        mock_form = FormDictFactory().create(hasEarliestLatest=False, returnDict=False)
        target_dict = Target.create_with_flight_local_time(
            mock_form.flightLocalTime, mock_form.toEvent, offsetLowAbsSec=3600, offsetHighAbsSec=10800).to_dict()
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
            "2018-12-17T08:26:40.000", True, offsetLowAbsSec=o_lo,
            offsetHighAbsSec=o_hi).to_dict()
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
            offsetLowAbsSec=o_lo,
            offsetHighAbsSec=o_hi).to_dict()
        expected_target_dict = Target.create_with_flight_local_time(
            "2018-12-17T08:26:40.000", True).to_dict()
        self.assertDictEqual(expected_target_dict, target_dict)

    #
    # def testCreateAirportTarget(self):
    #     mockForm = FormDictFactory.create(
    #         hasEarliestLatest=False, returnDict=False)
    #     targetDict = Target.create_with_form(mockForm).to_dict()
    #     valueExpected = {'eventCategory': 'airportRide',
    #                      'toEvent': True,
    #                      'arriveAtEventTime':
    #                          {'earliest': 1545066000, 'latest': 1545073200}}
    #     self.assertDictEqual(targetDict, valueExpected)
