from typing import Type

import iso8601
import pytz
from google.cloud.firestore import DocumentReference, transactional

import gravitate.domain.event_schedule.actions
from gravitate.domain.user import UserDao
from gravitate.domain.location import LocationGenericDao, AirportLocation
from gravitate.domain.event.dao import EventDao
from .models import Ride as RideRequest
from .dao import RideRequestGenericDao
from gravitate.forms.ride_request_creation_form import AirportRideRequestCreationForm
from gravitate.domain.user import User


def check_duplicate(user_id: str, event_ref: DocumentReference):
    """ Description Returns a boolean whether the user is trying to make a duplicate ride request

    :param user_id:
    :param event_ref:
    :return: True: it is a duplicate, False: it is not a duplicate
    """
    ride_requests = RideRequestGenericDao().get_by_user(user_id)
    event_doc_id = event_ref.id

    # Loop through each rideRequest
    for rideRequest in ride_requests:
        current_event_doc_id = rideRequest.event_ref.id
        if current_event_doc_id == event_doc_id:
            return True

    # No rideRequest has the same eventRef as the rideRequest that is about to be added
    return False


@transactional
def add_ride_request(transaction, ride_request, location, user_id, event=None):
    """ Description
        This method saves rideRequest and update user's eventSchedule.
        The method corresponds to use case "Create Ride Request".
        Note that transaction.commit() is not required after this method is called if this method is decorated
            by @transactional.

    :param transaction:
    :param ride_request:
    :param location:
    :param user_id:
    :return:
    """

    # Set the firestoreRef of the rideRequest
    RideRequestGenericDao().create(ride_request)
    # Saves RideRequest Object to Firestore
    RideRequestGenericDao().set_with_transaction(transaction, ride_request, ride_request.get_firestore_ref())
    # [START] Update the user's eventSchedule
    user_ref = UserDao().get_ref(user_id)
    # Build the eventSchedule for user
    event_schedule = gravitate.domain.event_schedule.actions.create_event_schedule(
        ride_request, location, event)
    UserDao.add_to_event_schedule_with_transaction(
        transaction, user_ref=user_ref, event_ref=ride_request.event_ref, event_schedule=event_schedule)
    # [END] Update the user's eventSchedule


def get_pickup_address(user_id) -> str:
    """
    This method returns the default pickup address of a user.
    :param user_id:
    :return:
    """
    user: User = UserDao().get_user_by_id(user_id)
    pickup_address = user.pickupAddress
    return pickup_address


def get_event_ref_by_id(event_id: str) -> DocumentReference:
    """
    This method returns the event_ref by event_id.
    :param event_id:
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


def get_airport_location(airport_code) -> AirportLocation:
    """ Description
        This method returns an airportLocation with airportCode.

    :param airport_code:
    :return:
    """
    return LocationGenericDao().find_by_airport_code(airport_code)


def find_event(flight_local_time) -> DocumentReference:
    """ Description
    1. Find event reference by querying events with flightLocalTime
    2. Return the reference of such event

    :param flight_local_time:
    :return:
    """

    # Parse the flightLocalTime of the ride request form, then query database 
    # event_time = local_time_as_timestamp(flight_local_time)
    event_date_str = local_time_as_date_str(flight_local_time)
    # eventReference = EventDao().locateAirportEvent(eventTime)
    event = EventDao().find_by_date_str(event_date_str, "airport")

    return event.get_firestore_ref()


def local_time_as_date_str(flight_local_time):
    tz = pytz.timezone("America/Los_Angeles")
    local_datetime = iso8601.parse_date(flight_local_time, default_timezone=None)
    # utc_datetime = tz.localize(local_datetime)  # TODO: test DST
    # utc_datetime = iso8601.parse_date(flight_local_time, default_timezone=None).astimezone(tz)
    return local_datetime.strftime("%Y-%m-%d")


def local_time_as_timestamp(flight_local_time):
    tz = pytz.timezone("America/Los_Angeles")
    local_datetime = iso8601.parse_date(flight_local_time, default_timezone=None)
    utc_datetime = tz.localize(local_datetime)  # TODO: test DST
    # utc_datetime = iso8601.parse_date(flight_local_time, default_timezone=None).astimezone(tz)
    return utc_datetime.timestamp()


def set_disabilities(form: AirportRideRequestCreationForm, rideRequestDict):
    """
        This method sets the accommodation options in rideRequest dict.
        Note that the method needs refactoring to pass values with parameters rather than structures.

    :param form:
    :param rideRequestDict:
    :return:
    """
    if 'disabilities' in form:
        # If 'disabilities' is defined in the form submitted
        rideRequestDict['disabilities'] = form['disabilities']
    else:
        # If 'disabilities' not defined, set an empty dict as value
        rideRequestDict['disabilities'] = dict()
