from gravitate.models import RideRequest, AirportRideRequest, SocialEventRideRequest, Location, Orbit, Event
from gravitate.data_access import RideRequestGenericDao, OrbitDao, UserDao, LocationGenericDao
from google.cloud.firestore import DocumentReference, Client, transactional, Transaction
from gravitate.controllers import eventscheduleutils
from typing import Type
from gravitate import config

db = config.Context.db


# @transactional
def joinOrbitToRideRequest(transaction: Transaction, rideRequest: Type[RideRequest],  orbit: Orbit) -> bool:
    """ Description
    This function joins a rideRequest to an orbit in the database. 
            Firstly, the function accesses database copy of the objects and download them as local copies
            Secondly, the function validates that the database copy of the object matches those passed along by the decision maker[1]
            Thirdly, the function modifies local copies so that a rideRequest is joined to an orbit
            Fourthly, the function updates database copy of the objects, and throw an error if they changed since last read

    [1] Note that decision maker should refresh local copies of the objects after each join, 
            since this function will raise an exception if they don't match. 

    :type rideRequestRef:DocumentReference:
    :param rideRequestRef:DocumentReference:

    :type orbitRef:DocumentReference:
    :param orbitRef:DocumentReference:

    :raises:

    :rtype:
    """

    # rideRequestDao = RideRequestGenericDao()
    # rideRequest = rideRequestDao.get_with_transaction(
    #     transaction, rideRequestRef)
    # rideRequest.set_firestore_ref(rideRequestRef)
    # orbitDao = OrbitDao()
    # orbit = orbitDao.get_with_transaction(transaction, orbitRef)
    # orbit.set_firestore_ref(orbitRef)

    # TODO: validate that rideRequest is the same as when the decision is made to join rideRequest to orbit
    # TODO: validate that orbit is the same as when the decision is made to join rideRequest to orbit

    if rideRequest.requestCompletion:
        return False

    # Modify local copies of rideRequest and orbit
    placeInOrbit(rideRequest, orbit)

    # Update database copy of rideRequest and orbit

    RideRequestGenericDao.set_with_transaction(
        transaction, rideRequest, rideRequest.get_firestore_ref())
    OrbitDao.set_with_transaction(
        transaction, orbit, orbit.get_firestore_ref())

    return True

class GroupOrbitInteractor(object):
    """
        TODO: replace functions with Command Pattern operations
    """

    def __init__(self):
        pass

def removeRideRequestFromOrbit(transaction, rideRequest: Type[RideRequest], orbit: Orbit) -> bool:

    removeFromOrbit(rideRequest, orbit)

    try:
        RideRequestGenericDao().set_with_transaction(
            transaction, rideRequest, rideRequest.get_firestore_ref())
        OrbitDao.set_with_transaction(
            transaction, orbit, orbit.get_firestore_ref())
    except Exception as e:
        print(e)
        return False

    return True


def updateEventSchedule(transaction: Transaction, rideRequest: RideRequest, orbit: Orbit, event: Event, location: Location):
    """ Description

            Populate eventSchedule (client view model)


    :type transaction:Transaction:
    :param transaction:Transaction:

    :type rideRequest:RideRequest:
    :param rideRequest:RideRequest:

    :type orbit:Orbit:
    :param orbit:Orbit:

    :raises:

    :rtype:
    """
    # update eventSchedule
    userId = rideRequest.userId
    userRef = UserDao().get_ref(userId)
    eventRef = event.get_firestore_ref()

    eventSchedule = eventscheduleutils.buildEventScheduleOrbit(
        rideRequest=rideRequest, location=location, orbit=orbit)
    UserDao().add_to_event_schedule_with_transaction(transaction,
                                                     userRef=userRef, eventRef=eventRef, eventSchedule=eventSchedule)


def placeInOrbit(r: RideRequest, o: Orbit):
    """ Description
            :type uid:str:
            :param uid:str:

            :type r:RideRequest:
            :param r:RideRequest:

            :type o:Orbit:
            :param o:Orbit:

            :raises:

            :rtype:
    """
    # set RideRequest's requestCompletion to true
    r.requestCompletion = True

    # RideRequest's orbitId no longer null and references Orbit's oId
    r.orbitRef = o.get_firestore_ref()

    userId = r.userId

    # fill in ticket and insert in to orbit's userTicketPairs
    ticket = {
        "rideRequestRef": r.get_firestore_ref(),
        "userWillDrive": r.driverStatus,
        "hasCheckedIn": False,
        "inChat": False,
        "pickupAddress": r.pickupAddress
    }
    o.userTicketPairs[userId] = ticket
    r.requestCompletion = True

    return


def removeFromOrbit(r: RideRequest, o: Orbit):
    # remove userRef from orbitRef's userTicketPairs
    # search userTicketPairs for userRef, remove userRef and corresponding ticket once done
    userIds = list(o.userTicketPairs.keys())
    for userId in userIds:
        if userId == r.userId:
            o.userTicketPairs.pop(userId)
    r.orbitRef = None
    r.requestCompletion = False
