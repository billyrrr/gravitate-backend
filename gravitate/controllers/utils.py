from gravitate.forms.ride_request_creation_form import AirportRideRequestCreationForm
from gravitate.models import AirportLocation, Event, RideRequest, AirportRideRequest, Target
from google.cloud.firestore import DocumentReference, Transaction, transactional
from gravitate.data_access import RideRequestGenericDao, EventDao, LocationGenericDao, UserDao
from . import eventscheduleutils

import iso8601
import datetime as dt
import pytz


def hasDuplicateEvent(userId: str, eventRef: DocumentReference):
    """ Description Returns a boolean whether the user is trying to make a duplicate ride request

    :param userId:
    :param eventRef:
    :return: True: it is a duplicate, False: it is not a duplicate
    """
    rideRequests = RideRequestGenericDao().getByUser(userId)
    eventDocId = eventRef.id

    # Loop through each rideRequest
    for rideRequest in rideRequests:
        currentEventDocId = rideRequest.eventRef.id
        if currentEventDocId == eventDocId:
            return True

    # No rideRequest has the same eventRef as the rideRequest that is about to be added
    return False


@transactional
def addRideRequest(transaction, rideRequest, location, userId):
    """ Description
        This method saves rideRequest and update user's eventSchedule.
        The method corresponds to use case "Create Ride Request".
        Note that transaction.commit() is not required after this method is called if this method is decorated
            by @transactional.

    :param transaction:
    :param rideRequest:
    :param location:
    :param userId:
    :return:
    """

    # Set the firestoreRef of the rideRequest
    RideRequestGenericDao().create(rideRequest)
    # Saves RideRequest Object to Firestore
    RideRequestGenericDao().setWithTransaction(transaction, rideRequest, rideRequest.getFirestoreRef())
    # [START] Update the user's eventSchedule
    userRef = UserDao().getRef(userId)
    # Build the eventSchedule for user
    eventSchedule = eventscheduleutils.buildEventSchedule(
        rideRequest, location)
    UserDao.addToEventScheduleWithTransaction(
        transaction, userRef=userRef, eventRef=rideRequest.eventRef, eventSchedule=eventSchedule)
    # [END] Update the user's eventSchedule


def createTarget(form: AirportRideRequestCreationForm):
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
    target = Target.createAirportEventTarget(form.toEvent, earliestTimestamp, latestTimestamp)
    return target


def createTargetWithFlightLocalTime(flightLocalTime, toEvent, offsetLowAbsSec: int = 7200,
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
    flightLocalTime = iso8601.parse_date(flightLocalTime, default_timezone=None).astimezone(tz)

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

    target = Target.createAirportEventTarget(toEvent, earliestTimestamp, latestTimestamp)

    return target


def getAirportLocation(airportCode) -> AirportLocation:
    """ Description
        This method returns an airportLocation with airportCode.

    :param airportCode:
    :return:
    """
    return LocationGenericDao().findByAirportCode(airportCode)


def findEvent(flight_local_time) -> DocumentReference:
    """ Description
    1. Find event reference by querying events with flightLocalTime
    2. Return the reference of such event

    :param flight_local_time:
    :return:
    """

    # Parse the flightLocalTime of the ride request form, then query database 
    eventTime = iso8601.parse_date(flight_local_time, default_timezone=None).timestamp()
    # eventReference = EventDao().locateAirportEvent(eventTime)
    event = EventDao().findByTimestamp(eventTime)

    return event.getFirestoreRef()


def setDisabilities(form: AirportRideRequestCreationForm, rideRequestDict):
    """
        This method sets the accommodation options in rideRequest dict.
        Note that the method needs refactoring to pass values with parameters rather than structures.

    :param form:
    :param rideRequestDict:
    :return:
    """
    if ('disabilities' in form):
        # If 'disabilities' is defined in the form submitted
        rideRequestDict['disabilities'] = form['disabilities']
    else:
        # If 'disabilities' not defined, set an empty dict as value
        rideRequestDict['disabilities'] = dict()
