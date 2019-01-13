from typing import Type

from google.cloud.firestore_v1beta1 import DocumentReference, transactional

from gravitate.controllers import eventscheduleutils
from gravitate.controllers.grouping import utils
from gravitate.controllers.grouping.grouping import db
from gravitate.controllers.grouping.utils import remove_from_orbit
from gravitate.data_access import RideRequestGenericDao, UserDao, OrbitDao, LocationGenericDao
from gravitate.models import RideRequest, Orbit


def remove(ride_request_ref: DocumentReference) -> bool:
    """
    This method removes/unmatches rideRequest from the orbit it associates with.

    :param ride_request_ref:
    :return: True if successful
    """
    transaction = db.transaction()
    _remove(transaction, ride_request_ref)
    return True


@transactional
def _remove(transaction, ride_request_ref: DocumentReference):
    """
    This method removes/unmatches rideRequest from the orbit it associates with.
    (Transactional business logic for use case unmatch from orbit)

    :param transaction:
    :param ride_request_ref:
    :return:
    """
    ride_request = RideRequestGenericDao().get_with_transaction(transaction, ride_request_ref)
    ride_request.set_firestore_ref(ride_request_ref)

    user_id = ride_request.user_id
    user_ref = UserDao().get_ref(user_id)
    # user = UserDao().get_user_with_transaction(transaction, userRef)

    orbit_ref = ride_request.orbit_ref

    assert orbit_ref is not None

    orbit_id = orbit_ref.id
    orbit = OrbitDao().get_with_transaction(transaction, orbit_ref)
    orbit.set_firestore_ref(orbit_ref)

    event_ref = orbit.event_ref

    # TODO: change to ride_request.location_ref
    location_ref: DocumentReference = ride_request.airport_location
    location = LocationGenericDao().get_with_transaction(transaction, location_ref)

    remove_ride_request_from_orbit(transaction, ride_request, orbit)

    # Delete current user eventSchedule that is associated with an orbit
    UserDao().remove_event_schedule_with_transaction(transaction, userRef=user_ref, orbitId=orbit_id)

    # TODO update eventSchedule of all participants

    # Build new eventSchedule that is not associated with any orbit and marked as pending
    event_schedule = eventscheduleutils.buildEventSchedule(ride_request, location=location)
    UserDao().add_to_event_schedule_with_transaction(transaction, user_ref=user_ref, event_ref=event_ref,
                                                     event_schedule=event_schedule)


def remove_ride_request_from_orbit(transaction, ride_request: Type[RideRequest], orbit: Orbit) -> bool:
    # DEPRECATED
    remove_from_orbit(ride_request, orbit)

    try:
        RideRequestGenericDao().set_with_transaction(
            transaction, ride_request, ride_request.get_firestore_ref())
        OrbitDao.set_with_transaction(
            transaction, orbit, orbit.get_firestore_ref())
    except Exception as e:
        print(e)
        return False

    return True