from typing import Type

from gravitate.forms.ride_request_creation_form import AirportRideRequestCreationForm
from gravitate.models import AirportLocation, RideRequest, User
from google.cloud.firestore import DocumentReference, transactional
from gravitate.data_access import RideRequestGenericDao, EventDao, LocationGenericDao, UserDao
from . import eventscheduleutils

import iso8601
import pytz


def hasDuplicateEvent(userId: str, eventRef: DocumentReference):
    """ Description Returns a boolean whether the user is trying to make a duplicate ride request

    :param userId:
    :param eventRef:
    :return: True: it is a duplicate, False: it is not a duplicate
    """
    rideRequests = RideRequestGenericDao().get_by_user(userId)
    eventDocId = eventRef.id

    # Loop through each rideRequest
    for rideRequest in rideRequests:
        currentEventDocId = rideRequest.event_ref.id
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
    RideRequestGenericDao().set_with_transaction(transaction, rideRequest, rideRequest.get_firestore_ref())
    # [START] Update the user's eventSchedule
    userRef = UserDao().get_ref(userId)
    # Build the eventSchedule for user
    eventSchedule = eventscheduleutils.buildEventSchedule(
        rideRequest, location)
    UserDao.add_to_event_schedule_with_transaction(
        transaction, userRef=userRef, eventRef=rideRequest.event_ref, eventSchedule=eventSchedule)
    # [END] Update the user's eventSchedule


def get_pickup_address(userId) -> str:
    """
    This method returns the default pickup address of a user.
    :param userId:
    :return:
    """
    user: User = UserDao().get_user_by_id(userId)
    pickup_address = user.pickupAddress
    return pickup_address


def get_event_ref_by_id(event_id: str) -> DocumentReference:
    """
    This method returns the event_ref by event_id.
    :param eventId:
    :return: DocumentReference of the event.
    """
    return EventDao().get_ref(event_id)


def get_location_ref_by_id(location_id: str) -> DocumentReference:
    """
    This method return the location_ref by location_id.
    :param location_id:
    :return:
    """
    return LocationGenericDao().get_ref_by_id(location_id)


def get_ride_request(d: dict) -> Type[RideRequest]:
    ride_request = RideRequest.from_dict(d)
    return ride_request


def getAirportLocation(airportCode) -> AirportLocation:
    """ Description
        This method returns an airportLocation with airportCode.

    :param airportCode:
    :return:
    """
    return LocationGenericDao().find_by_airport_code(airportCode)


def findEvent(flight_local_time) -> DocumentReference:
    """ Description
    1. Find event reference by querying events with flightLocalTime
    2. Return the reference of such event

    :param flight_local_time:
    :return:
    """

    # Parse the flightLocalTime of the ride request form, then query database 
    eventTime = local_time_as_timestamp(flight_local_time)
    # eventReference = EventDao().locateAirportEvent(eventTime)
    event = EventDao().find_by_timestamp(eventTime, "airport")

    return event.get_firestore_ref()


def local_time_as_timestamp(flight_local_time):
    tz = pytz.timezone("America/Los_Angeles")
    local_datetime = iso8601.parse_date(flight_local_time, default_timezone=None)
    utc_datetime = tz.localize(local_datetime)  # TODO: test DST
    # utc_datetime = iso8601.parse_date(flight_local_time, default_timezone=None).astimezone(tz)
    return utc_datetime.timestamp()


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
