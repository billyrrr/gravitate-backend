from models.ride_request import RideRequest, AirportRideRequest, Target
from forms.ride_request_creation_form import RideRequestCreationForm
from google.cloud.firestore import DocumentReference, Transaction
from data_access.ride_request_dao import RideRequestGenericDao
from data_access.event_dao import EventGenericDao
from datetime import datetime, timezone
import pytz

def saveRideRequest(rideRequest, transaction: Transaction = None):
        if (rideRequest.getFirestoreRef()):
            if not transaction:
                raise Exception('transaction is not provided. ')
            RideRequestGenericDao().setRideRequestWithTransaction(transaction, rideRequest, rideRequest.getFirestoreRef())
        else:
            newRef = RideRequestGenericDao().createRideRequest(rideRequest)
            rideRequest.setFirestoreRef(newRef)

def createTarget(form: RideRequestCreationForm):
    """
    Note that this method won't work if any datetime string represents a time when
        daylight saving ends (November 4 1:00AM-2:00AM). 
        since anytime in between corresponds to more than one possible UTC time. 

        :param form:RideRequestCreationForm: 
    """
    tz = pytz.timezone('America/Los_Angeles')
    earliestDatetime = datetime.fromisoformat(form.earliest).astimezone(tz)
    earliestTimestamp = int(earliestDatetime.timestamp())
    latestDatetime = datetime.fromisoformat(form.latest).astimezone(tz)
    latestTimestamp = int(latestDatetime.timestamp())
    # TODO: retrieve tzinfo from event rather than hardcoding 'America/Los_Angeles'
    target = Target.createAirportEventTarget(form.toEvent, earliestTimestamp, latestTimestamp)
    return target

def findLocation(form: RideRequestCreationForm) -> DocumentReference:
    """ Description
        This function finds the locationRef for "LAX" or other airportLocation(s)

    :type form:RideRequestCreationForm:
    :param form:RideRequestCreationForm:

    :raises:

    :rtype:
    """

    # TODO [to assign] implement
    
    return "/mocklocation" # TODO change

def findEvent(form: RideRequestCreationForm) -> str:
    """ Description
    1. Find event reference by querying events with flightLocalTime
    2. Return the reference of such event

    :type form:RideRequestCreationForm:
    :param form:RideRequestCreationForm:

    :raises:

    :rtype:
    """
    # Parse the flightLocalTime of the ride request form, then query database
    tz = pytz.timezone('America/Los_Angeles') 
    eventTz = (datetime.fromisoformat(form.flightLocalTime)).astimezone(tz)
    eventTime = eventTz.timestamp()
    eventReference = EventGenericDao().locateAirportEvent(form.toEvent(), eventTime)

    return eventReference

def setDisabilities(form: RideRequestCreationForm, rideRequestDict):
    if ('disabilities' in form):
        # If 'disabilities' is defined in the form submitted
        rideRequestDict['disabilities'] = form['disabilities']
    else:
        # If 'disabilities' not defined, set an empty dict as value
        rideRequestDict['disabilities'] = dict()
