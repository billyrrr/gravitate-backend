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

    earliestDatetime = iso8601.parse_date(form.earliest, default_timezone=None).astimezone(tz)
    latestDatetime = iso8601.parse_date(form.latest, default_timezone=None).astimezone(tz)

    earliestTimestamp = int(earliestDatetime.timestamp())
    latestTimestamp = int(latestDatetime.timestamp())
    # TODO: retrieve tzinfo from event rather than hardcoding 'America/Los_Angeles'
    target = Target.create_airport_event_target(form.toEvent, earliestTimestamp, latestTimestamp)
    return target


def create_target_with_flight_local_time(flightLocalTime, toEvent, offsetLowAbsSec: int = 7200,
                                  offsetHighAbsSec: int = 18000):
    """
        This method creates a target with flightLocal Time. The offsets represents how much in advance
            is user's preferred earliest and latest.

        Limitations:
            this method won't work if any datetime string represents a time when
                daylight saving ends (November 4 1:00AM-2:00AM).
                since anytime in between corresponds to more than one possible UTC time.

    :param flightLocalTime:
    :param toEvent:
    :param offsetLowAbsSec: The offset with lower absolute value.
    :param offsetHighAbsSec: The offset with higher absolute value.
    :return:
    """
    assert offsetLowAbsSec >= 0
    assert offsetHighAbsSec >= 0
    # Check that offsetLow represents a greater than or equal to interval than offsetHigh
    assert offsetLowAbsSec <= offsetHighAbsSec
    # Check that there earliest and latest represents a range of time
    assert offsetLowAbsSec != offsetHighAbsSec

    tz = pytz.timezone('America/Los_Angeles')
    flightLocalTime = tz.localize(iso8601.parse_date(flightLocalTime, default_timezone=None))

    # Get timedelta object with seconds
    offsetEarlierAbs = dt.timedelta(seconds=offsetHighAbsSec)
    offsetLaterAbs = dt.timedelta(seconds=offsetLowAbsSec)

    # Get earliest and latest datetime
    earliest: dt.datetime = flightLocalTime - offsetEarlierAbs
    latest: dt.datetime = flightLocalTime - offsetLaterAbs

    earliestTimestamp = int(earliest.timestamp())
    latestTimestamp = int(latest.timestamp())

    assert earliestTimestamp <= latestTimestamp  # Check that "earliest" occurs earliest than "latest"
    assert earliestTimestamp != latestTimestamp  # Check that "earliest" is not the same as latest

    target = Target.create_airport_event_target(toEvent, earliestTimestamp, latestTimestamp)

    return target


class Target(FirestoreObject):

    def __init__(self, eventCategory):
        self.eventCategory = eventCategory

    create_with_flight_local_time = create_target_with_flight_local_time
    create_with_form = create_target_with_form

    @staticmethod
    def from_dict(targetDict: dict):
        toEvent = targetDict['toEvent']
        if (toEvent):
            return ToEventTarget(targetDict['eventCategory'], targetDict['arriveAtEventTime'])
        else:
            return FromEventTarget(targetDict['eventCategory'], targetDict['leaveEventTime'])

    @staticmethod
    def create_airport_event_target(toEvent: bool, earliest:int, latest:int):
        if (toEvent):
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

    def to_dict(self):
        """ Description
            This function returns a dictionary of the target. 

        :type self:
        :param self:
    
        :raises:
    
        :rtype:
        """ 
        targetDict = {
            u'eventCategory': self.eventCategory
        }
        return targetDict


class ToEventTarget(Target):

    def __init__(self, eventCategory, arriveAtEventTime):
        super().__init__(eventCategory)
        self.arriveAtEventTime = arriveAtEventTime

    def to_dict(self):
        targetDict = super().to_dict()
        targetDict[u'toEvent'] = True
        targetDict[u'arriveAtEventTime'] = self.arriveAtEventTime
        return targetDict


class FromEventTarget(Target):

    def __init__(self, eventCategory, leaveEventTime):
        super().__init__(eventCategory)
        self.leaveEventTime = leaveEventTime

    def to_dict(self):
        targetDict = super().to_dict()
        targetDict[u'toEvent'] = False
        targetDict[u'leaveEventTime'] = self.leaveEventTime
        return targetDict

