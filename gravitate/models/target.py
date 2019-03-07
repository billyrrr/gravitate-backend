import datetime as dt
from typing import Type

import iso8601
import pytz

from gravitate.forms.ride_request_creation_form import AirportRideRequestCreationForm
from .firestore_object import FirestoreObject

# TODO: refactor to Business Object


def create_target_with_form(form: AirportRideRequestCreationForm):
    """
    Note that this method won't work if any datetime string represents a time when
        daylight saving ends (November 4 1:00AM-2:00AM).
        since anytime in between corresponds to more than one possible UTC time.

        :param form:AirportRideRequestCreationForm:
    """
    tz = pytz.timezone('America/Los_Angeles')

    earliest_datetime = iso8601.parse_date(form.earliest, default_timezone=None).astimezone(tz)
    latest_datetime = iso8601.parse_date(form.latest, default_timezone=None).astimezone(tz)

    earliest_timestamp = int(earliest_datetime.timestamp())
    latest_timestamp = int(latest_datetime.timestamp())
    # TODO: retrieve tzinfo from event rather than hard-coding 'America/Los_Angeles'
    target = Target.create_airport_event_target(form.toEvent, earliest_timestamp, latest_timestamp)
    return target


def create_target_with_flight_local_time(flight_local_time, to_event, offset_low_abs_sec: int = 7200,
                                         offset_high_abs_sec: int = 18000):
    """
        This method creates a target with flightLocal Time. The offsets represents how much in advance
            is user's preferred earliest and latest.

        Limitations:
            this method won't work if any datetime string represents a time when
                daylight saving ends (November 4 1:00AM-2:00AM).
                since anytime in between corresponds to more than one possible UTC time.

    :param flight_local_time:
    :param to_event:
    :param offset_low_abs_sec: The offset with lower absolute value.
    :param offset_high_abs_sec: The offset with higher absolute value.
    :return:
    """
    assert offset_low_abs_sec >= 0
    assert offset_high_abs_sec >= 0
    # Check that offsetLow represents a greater than or equal to interval than offsetHigh
    assert offset_low_abs_sec <= offset_high_abs_sec
    # Check that there earliest and latest represents a range of time
    assert offset_low_abs_sec != offset_high_abs_sec

    tz = pytz.timezone('America/Los_Angeles')
    flight_local_time = tz.localize(iso8601.parse_date(flight_local_time, default_timezone=None))

    # Get timedelta object with seconds
    offset_earlier_abs = dt.timedelta(seconds=offset_high_abs_sec)
    offset_later_abs = dt.timedelta(seconds=offset_low_abs_sec)

    # Get earliest and latest datetime
    earliest: dt.datetime = flight_local_time - offset_earlier_abs
    latest: dt.datetime = flight_local_time - offset_later_abs

    earliest_timestamp = int(earliest.timestamp())
    latest_timestamp = int(latest.timestamp())

    assert earliest_timestamp <= latest_timestamp  # Check that "earliest" occurs earliest than "latest"
    assert earliest_timestamp != latest_timestamp  # Check that "earliest" is not the same as latest

    target = Target.create_airport_event_target(to_event, earliest_timestamp, latest_timestamp)

    return target


class Target(FirestoreObject):

    def __init__(self, event_category):
        self.event_category = event_category
        self.to_event = None

    create_with_flight_local_time = create_target_with_flight_local_time
    create_with_form = create_target_with_form

    @staticmethod
    def from_dict(target_dict: dict):
        to_event = target_dict['toEvent']
        if (to_event):
            return ToEventTarget(target_dict['eventCategory'], target_dict['arriveAtEventTime'])
        else:
            return FromEventTarget(target_dict['eventCategory'], target_dict['leaveEventTime'])

    @staticmethod
    def create_airport_event_target(to_event: bool, earliest: int, latest: int):
        if (to_event):
            return ToEventTarget('airportRide', {
                'earliest': earliest,
                'latest': latest,
                # TODO add timezone
            })
        else:
            return FromEventTarget('airportRide', {
                'earliest': earliest,
                'latest': latest
            })

    @staticmethod
    def create_social_event_target(to_event: bool, earliest: int, latest: int):
        if (to_event):
            return ToEventTarget('eventRide', {
                'earliest': earliest,
                'latest': latest,
                # TODO add timezone
            })
        else:
            return FromEventTarget('eventRide', {
                'earliest': earliest,
                'latest': latest
            })

    def to_dict(self):
        """ Description
            This function returns a dictionary of the target. 

        :type self:
        :param self:
    
        :raises:
    
        :rtype:
        """ 
        target_dict = {
            u'eventCategory': self.event_category
        }
        return target_dict


class ToEventTarget(Target):

    def __init__(self, event_category, arrive_at_event_time):
        super().__init__(event_category)
        self.to_event = True
        self.arrive_at_event_time = arrive_at_event_time

    def to_dict(self):
        target_dict = super().to_dict()
        target_dict[u'toEvent'] = True
        target_dict[u'arriveAtEventTime'] = self.arrive_at_event_time
        return target_dict


class FromEventTarget(Target):

    def __init__(self, event_category, leave_event_time):
        super().__init__(event_category)
        self.to_event = False
        self.leave_event_time = leave_event_time

    def to_dict(self):
        target_dict = super().to_dict()
        target_dict[u'toEvent'] = False
        target_dict[u'leaveEventTime'] = self.leave_event_time
        return target_dict

