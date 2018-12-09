from forms.ride_request_creation_form import RideRequestCreationForm
from models import AirportLocation, Event, RideRequest, AirportRideRequest, Target
from google.cloud.firestore import DocumentReference, Transaction, transactional
from data_access.ride_request_dao import RideRequestGenericDao
from data_access.event_dao import EventDao
from data_access.location_dao import LocationGenericDao
import iso8601
import datetime as dt
import pytz

import random 
import string 
  
# Generate a random string 
# with 32 characters. 
# https://www.geeksforgeeks.org/generating-random-ids-python/
def randomId():
    randomIdStr = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]) 
    return randomIdStr

@transactional
def saveRideRequest(transaction, rideRequest):
        if (rideRequest.getFirestoreRef()):
            if not transaction:
                raise Exception('transaction is not provided. ')
            RideRequestGenericDao().setWithTransaction(transaction, rideRequest, rideRequest.getFirestoreRef())
        else:
            newRef = RideRequestGenericDao().create(rideRequest)
            rideRequest.setFirestoreRef(newRef)

def hasDuplicateEvent(userId: str, eventRef: DocumentReference):
    """
        Description: Returns a boolean whether the user is trying to make a duplicate ride request
        True: it is a duplicate, 
        False: it is not a duplicate
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


def createTarget(form: RideRequestCreationForm):
    """
    Note that this method won't work if any datetime string represents a time when
        daylight saving ends (November 4 1:00AM-2:00AM). 
        since anytime in between corresponds to more than one possible UTC time. 

        :param form:RideRequestCreationForm: 
    """
    tz = pytz.timezone('America/Los_Angeles')

    earliestDatetime = iso8601.parse_date(form.earliest, default_timezone=None).astimezone(tz)
    latestDatetime = iso8601.parse_date(form.latest, default_timezone=None).astimezone(tz)

    earliestTimestamp = int(earliestDatetime.timestamp())
    latestTimestamp = int(latestDatetime.timestamp())
    # TODO: retrieve tzinfo from event rather than hardcoding 'America/Los_Angeles'
    target = Target.createAirportEventTarget(form.toEvent, earliestTimestamp, latestTimestamp)
    return target

def createTargetWithFlightLocalTime(form: RideRequestCreationForm, offsetLowAbsSec: int = 7200, offsetHighAbsSec: int = 18000):
    assert offsetLowAbsSec >= 0
    assert offsetHighAbsSec >= 0
    assert offsetLowAbsSec <= offsetHighAbsSec # Check that offsetLow represents a greater than or equal to interval than offsetHigh
    assert offsetLowAbsSec != offsetHighAbsSec # Check that there earliest and latest represents a range of time

    tz = pytz.timezone('America/Los_Angeles')
    flightLocalTime = iso8601.parse_date(form.flightLocalTime, default_timezone=None).astimezone(tz)

    # Get timedelta object with seconds
    offsetEarlierAbs = dt.timedelta(seconds=offsetHighAbsSec)
    offsetLaterAbs = dt.timedelta(seconds=offsetLowAbsSec)

    # Get earliest and latest datetime
    earliest: dt.datetime = flightLocalTime - offsetEarlierAbs
    latest: dt.datetime = flightLocalTime - offsetLaterAbs
    
    earliestTimestamp = int(earliest.timestamp())
    latestTimestamp = int(latest.timestamp())

    assert earliestTimestamp <= latestTimestamp # Check that "earliest" occurs earliest than "latest"
    assert earliestTimestamp != latestTimestamp # Check that "earliest" is not the same as latest

    target = Target.createAirportEventTarget(form.toEvent, earliestTimestamp, latestTimestamp)

    return target


def findLocation(form: RideRequestCreationForm) -> DocumentReference:
    """ Description
        **DEPRECATED**
        This function finds the locationRef for "LAX" or other airportLocation(s)

    :type form:RideRequestCreationForm:
    :param form:RideRequestCreationForm:

    :raises:

    :rtype:
    """
    return LocationGenericDao().findByAirportCode(form.airportCode).getFirestoreRef()

def getAirportLocation(form: RideRequestCreationForm) -> AirportLocation:
    return LocationGenericDao().findByAirportCode(form.airportCode)

def mockFindLocation(form: RideRequestCreationForm) -> str:
    return '/locations/testairportlocationid1'

def findEvent(form: RideRequestCreationForm) -> DocumentReference:
    
    """ Description
    1. Find event reference by querying events with flightLocalTime
    2. Return the reference of such event

    :type form:RideRequestCreationForm:
    :param form:RideRequestCreationForm:

    :raises:

    :rtype:
    """
    # Parse the flightLocalTime of the ride request form, then query database 
    eventTime = iso8601.parse_date(form.flightLocalTime, default_timezone=None).timestamp()
    # eventReference = EventDao().locateAirportEvent(eventTime)
    event = EventDao().findByTimestamp(eventTime)

    return event.getFirestoreRef()

def mockFindEvent(form: RideRequestCreationForm) -> str:

    # Query to locate proper Event. Supposed to be only one for airport ride

    """     # Event found and parsed from snapshot returned by query (not neccessary)
        event = Event.fromDict({
                "eventCategory": "airport",
                "participants": [
                        "refU01",
                        "refU02"
                ],
                "eventLocation": "refL01",
                "locationRefs": [],
                "startTimestamp": 1545033600,
                "endTimestamp": 1545119999,
                "pricing": 100
        }) """

    # eventRef of type DocumentReference as returned by query
    eventRef = '/events/testeventid1'
    return eventRef

def setDisabilities(form: RideRequestCreationForm, rideRequestDict):
    if ('disabilities' in form):
        # If 'disabilities' is defined in the form submitted
        rideRequestDict['disabilities'] = form['disabilities']
    else:
        # If 'disabilities' not defined, set an empty dict as value
        rideRequestDict['disabilities'] = dict()
