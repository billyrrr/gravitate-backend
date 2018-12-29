from gravitate.models import RideRequest, Location, Orbit, Event
from gravitate.data_access import RideRequestGenericDao, OrbitDao, UserDao
from google.cloud.firestore import Transaction
from gravitate.controllers import eventscheduleutils
from typing import Type
from gravitate import context

db = context.Context.db


def join_orbit_to_ride_request(ride_request: Type[RideRequest], orbit: Orbit) -> bool:
    """ Description
    This function joins a rideRequest to an orbit in the database.
            Firstly, the function accesses database copy of the objects and download them as local copies
            Secondly, the function validates that the database copy of the object matches those passed along by the decision maker[1]
            Thirdly, the function modifies local copies so that a rideRequest is joined to an orbit
            Fourthly, the function updates database copy of the objects, and throw an error if they changed since last read

    [1] Note that decision maker should refresh local copies of the objects after each join,
            since this function will raise an exception if they don't match.

    :param ride_request:
    :param orbit:
    :return:
    """
    # TODO: validate that rideRequest is the same as when the decision is made to join rideRequest to orbit
    # TODO: validate that orbit is the same as when the decision is made to join rideRequest to orbit

    if ride_request.request_completion:
        return False
    pairs: dict = orbit.user_ticket_pairs
    for user_id, ticket in pairs.items():
        if ticket["userWillDrive"] and ride_request.driver_status:
            # There is already an I-4 driver. Do not join another driver to the orbit
            return False

    # Modify local copies of rideRequest and orbit
    place_in_orbit(ride_request, orbit)

    return True


class GroupOrbitInteractor(object):
    """
        TODO: replace functions with Command Pattern operations
    """

    def __init__(self):
        pass


def remove_ride_request_from_orbit(transaction, ride_request: Type[RideRequest], orbit: Orbit) -> bool:
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


def update_event_schedule(transaction: Transaction, ride_request: RideRequest, orbit: Orbit, event: Event,
                          location: Location):
    """ Description

            Populate eventSchedule (client view model)


    :type transaction:Transaction:
    :param transaction:Transaction:

    :type ride_request:RideRequest:
    :param ride_request:RideRequest:

    :type orbit:Orbit:
    :param orbit:Orbit:

    :raises:

    :rtype:
    """
    # update eventSchedule
    user_id = ride_request.user_id
    user_ref = UserDao().get_ref(user_id)
    event_ref = event.get_firestore_ref()

    event_schedule = eventscheduleutils.buildEventScheduleOrbit(
        rideRequest=ride_request, location=location, orbit=orbit)
    UserDao().add_to_event_schedule_with_transaction(transaction,
                                                     user_ref=user_ref,
                                                     event_ref=event_ref,
                                                     event_schedule=event_schedule)


def place_in_orbit(r: RideRequest, o: Orbit):
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


def remove_from_orbit(r: RideRequest, o: Orbit):
    # remove userRef from orbitRef's userTicketPairs
    # search userTicketPairs for userRef, remove userRef and corresponding ticket once done
    userIds = list(o.user_ticket_pairs.keys())
    for userId in userIds:
        if userId == r.user_id:
            o.user_ticket_pairs.pop(userId)
    r.orbit_ref = None
    r.request_completion = False
