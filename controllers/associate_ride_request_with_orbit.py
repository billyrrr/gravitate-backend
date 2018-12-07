from models import RideRequest, AirportRideRequest, SocialEventRideRequest, Location, Orbit, Event
from data_access import RideRequestGenericDao, OrbitDao, UserDao, LocationGenericDao
from google.cloud.firestore import DocumentReference, Client, transactional, Transaction
from controllers import  eventscheduleutils
from typing import Type
import config

db = config.Context.db

@transactional
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
    # rideRequest = rideRequestDao.getWithTransaction(
    #     transaction, rideRequestRef)
    # rideRequest.setFirestoreRef(rideRequestRef)
    # orbitDao = OrbitDao()
    # orbit = orbitDao.getWithTransaction(transaction, orbitRef)
    # orbit.setFirestoreRef(orbitRef)

    # TODO: validate that rideRequest is the same as when the decision is made to join rideRequest to orbit
    # TODO: validate that orbit is the same as when the decision is made to join rideRequest to orbit

    if rideRequest.requestCompletion:
        return False

    # Modify local copies of rideRequest and orbit
    placeInOrbit(rideRequest, orbit)

    # Update database copy of rideRequest and orbit
    try:
        
        RideRequestGenericDao.setWithTransaction(transaction, rideRequest, rideRequest.getFirestoreRef())
        OrbitDao.setWithTransaction(transaction, orbit, orbit.getFirestoreRef())

    except Exception as e:
        print(e)
        return False

    return True

@transactional
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
    userRef = UserDao().getRef(userId)
    eventRef = event.getFirestoreRef()

    eventSchedule = eventscheduleutils.buildEventScheduleOrbit(rideRequest=rideRequest, location=location, orbit=orbit)
    UserDao().addToEventScheduleWithTransaction(transaction, userRef=userRef, eventRef=eventRef, eventSchedule=eventSchedule)

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
    r.orbitRef = o.getFirestoreRef()

    userId = r.userId

    # fill in ticket and insert in to orbit's userTicketPairs
    ticket = {
            "rideRequestRef": r.getFirestoreRef(),
            "userWillDrive": r.driverStatus,
            "hasCheckedIn": False,
            "inChat": False,
            "pickupAddress": r.pickupAddress
    }
    o.userTicketPairs[userId] = ticket
    r.requestCompletion = True

    return
