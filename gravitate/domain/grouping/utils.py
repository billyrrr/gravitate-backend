# import gravitate.domain.event_schedule.actions
from gravitate.models import RideRequest, Location, Orbit, Event
from gravitate.data_access import UserDao
from google.cloud.firestore import Transaction
from gravitate.domain.event_schedule import actions as event_schedule_actions
from typing import Type
from gravitate import context

db = context.Context.db


def add_orbit_to_ride_request(ride_request: Type[RideRequest], orbit: Orbit) -> bool:
    """ Returns True if ride request object and orbit is modified. False if join is not permitted.

    :param ride_request:
    :param orbit:
    :return:
    """
    # TODO: validate that rideRequest is the same as when the decision is made to join rideRequest to orbit
    # TODO: validate that orbit is the same as when the decision is made to join rideRequest to orbit

    is_valid = _validate_to_add(ride_request, orbit)
    if is_valid:

        # Modify local copies of rideRequest and orbit
        _add_to_orbit(ride_request, orbit)

        return True

    else:

        return False


def _validate_to_add(ride_request: Type[RideRequest], orbit: Orbit):
    """ Returns True if add operation is considered valid.

    :param ride_request:
    :param orbit:
    :return:
    """
    if ride_request.request_completion:
        return False
    pairs: dict = orbit.user_ticket_pairs
    for user_id, ticket in pairs.items():
        if ticket["userWillDrive"] and ride_request.driver_status:
            # There is already an I-4 driver. Do not join another driver to the orbit
            return False
    return True


def _add_to_orbit(r: RideRequest, o: Orbit):
    """ Description

            :type r:RideRequest:
            :param r:RideRequest:

            :type o:Orbit:
            :param o:Orbit:

            :raises:

            :rtype:
    """
    # set RideRequest's requestCompletion to true
    r.request_completion = True

    # RideRequest's orbitId no longer null and references Orbit's oId
    r.orbit_ref = o.get_firestore_ref()

    user_id = r.user_id

    # fill in ticket and insert in to orbit's userTicketPairs
    ticket = {
        "rideRequestRef": r.get_firestore_ref(),
        "userWillDrive": r.driver_status,
        "hasCheckedIn": False,
        "inChat": False,
        "pickupAddress": r.pickup_address
    }
    o.user_ticket_pairs[user_id] = ticket
    r.request_completion = True

    return


def drop_orbit_from_ride_request(ride_request: Type[RideRequest], orbit: Orbit) -> bool:
    """ Returns True if ride request object and orbit is modified. False if drop is not permitted.

    :param ride_request:
    :param orbit:
    :return:
    """
    # TODO: validate that rideRequest is the same as when the decision is made to join rideRequest to orbit
    # TODO: validate that orbit is the same as when the decision is made to join rideRequest to orbit

    is_valid = _validate_to_drop(ride_request, orbit)
    if is_valid:

        # Modify local copies of rideRequest and orbit
        _drop_from_orbit(ride_request, orbit)

        return True

    else:

        return False


def _validate_to_drop(ride_request: Type[RideRequest], orbit: Orbit):
    """ Returns True if drop operation is considered valid.
    TODO: add more
    :param ride_request:
    :param orbit:
    :return:
    """
    if not ride_request.request_completion:
        # If the ride request is not completed
        return False

    return True


def _drop_from_orbit(r: RideRequest, o: Orbit):
    # remove userRef from orbitRef's userTicketPairs
    # search userTicketPairs for userRef, remove userRef and corresponding ticket once done
    userIds = list(o.user_ticket_pairs.keys())
    for userId in userIds:
        if userId == r.user_id:
            o.user_ticket_pairs.pop(userId)
    r.orbit_ref = None
    r.request_completion = False


def update_in_orbit_event_schedule(transaction: Transaction, ride_request: Type[RideRequest], orbit: Orbit,
                                   event: Event, location: Location):
    """ Populate eventSchedule (client view model)
    :param transaction:
    :param ride_request:
    :param orbit:
    :param event:
    :param location:
    :return:
    """

    # update eventSchedule
    user_id = ride_request.user_id
    user_ref = UserDao().get_ref(user_id)
    event_ref = event.get_firestore_ref()

    event_schedule = event_schedule_actions.create_event_schedule_orbit(
        ride_request=ride_request, location=location, orbit=orbit)
    UserDao().add_to_event_schedule_with_transaction(transaction,
                                                     user_ref=user_ref,
                                                     event_ref=event_ref,
                                                     event_schedule=event_schedule)


def update_not_in_orbit_event_schedule(transaction: Transaction, ride_request: RideRequest, event: Event,
                                       location: Location):
    # update eventSchedule
    user_id = ride_request.user_id
    user_ref = UserDao().get_ref(user_id)
    event_ref = event.get_firestore_ref()

    event_schedule = event_schedule_actions.create_event_schedule(ride_request, location)
    UserDao().add_to_event_schedule_with_transaction(transaction,
                                                     user_ref=user_ref,
                                                     event_ref=event_ref,
                                                     event_schedule=event_schedule)


def remove_from_orbit(r: RideRequest, o: Orbit):
    # DEPRECATED
    # remove userRef from orbitRef's userTicketPairs
    # search userTicketPairs for userRef, remove userRef and corresponding ticket once done
    userIds = list(o.user_ticket_pairs.keys())
    for userId in userIds:
        if userId == r.user_id:
            o.user_ticket_pairs.pop(userId)
    r.orbit_ref = None
    r.request_completion = False


class GroupOrbitInteractor(object):
    """
        TODO: replace functions with Command Pattern operations
    """

    def __init__(self):
        pass
