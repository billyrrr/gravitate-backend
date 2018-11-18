from models.ride_request import RideRequest, AirportRideRequest, Target
from forms.ride_request_creation_form import RideRequestCreationForm
from ride_request_service.exceptions import *
from google.cloud.firestore import DocumentReference
from datetime import datetime, timezone
import pytz


def buildAirportRideRequestWithForm(form: RideRequestCreationForm) -> AirportRideRequest:

    rideRequestDict = dict()
    
    rideRequestDict['rideCategory'] = 'airportRide'

    # Move data from the form frontend submitted to rideRequestDict
    rideRequestDict['pickupAddress'] = form.pickupAddress
    rideRequestDict['driverStatus'] = form.driverStatus
    rideRequestDict['flightLocalTime'] = form.flightLocalTime
    rideRequestDict['flightNumber'] = form.flightNumber

    # Fields to be filled "immediately"

    # TODO fill unspecified options with default values
    rideRequestDict['pricing'] = 987654321 # TODO change

    # Populate rideRequestDict with default service data
    rideRequestDict['disabilities'] = dict()
    rideRequestDict['baggages'] = dict()
    rideRequestDict['hasCheckedIn'] = False
    rideRequestDict['orbitRef'] = None

    # Fields to be filled "after some thinking"

    # Set Target
    target = createTarget(form)
    rideRequestDict['target'] = target.toDict()

    # Set EventRef
    eventRef: DocumentReference = findEvent(form)
    if (eventRef):
        rideRequestDict['eventRef'] = eventRef
    else:
        raise EventNotFoundException('Cannot find event corresponding to the flightLocalTime. ')
    
    airportLocationRef: DocumentReference = findLocation(form)
    rideRequestDict['airportLocation'] = airportLocationRef

    rideRequest: AirportRideRequest = RideRequest.fromDict(rideRequestDict)

    return rideRequest

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
    # TODO [to assign]

    return None

def findEvent(form: RideRequestCreationForm) -> DocumentReference:
    # TODO [to assign] 
    
    """ Description
    1. Find event reference by querying events with flightLocalTime
    2. Return the reference of such event

    :type form:RideRequestCreationForm:
    :param form:RideRequestCreationForm:

    :raises:

    :rtype:
    """
    return None

def setDisabilities(form: RideRequestCreationForm, rideRequestDict):
    if ('disabilities' in form):
        # If 'disabilities' is defined in the form submitted
        rideRequestDict['disabilities'] = form['disabilities']
    else:
        # If 'disabilities' not defined, set an empty dict as value
        rideRequestDict['disabilities'] = dict()