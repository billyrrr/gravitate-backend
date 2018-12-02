from models.orbit import Orbit
from models.ride_request import RideRequest, AirportRideRequest, SocialEventRideRequest
from data_access.ride_request_dao import RideRequestGenericDao
from data_access.orbit_dao import OrbitDao
from google.cloud.firestore import DocumentReference, Client
from usersHelper.placeInOrbit import placeInOrbit
from typing import Type
import config

db = config.Context.db

def joinOrbitToRideRequest(rideRequestRef: DocumentReference, preDecisionRideRequest: Type[RideRequest],
                           orbitRef: DocumentReference, preDecisionOrbit: Orbit):
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

    # Create a transaction so that an exception is thrown when updating an object that is changed since last read from database
    transaction = db.transaction()

    rideRequestDao = RideRequestGenericDao()
    rideRequest = rideRequestDao.getRideRequestWithTransaction(
        transaction, rideRequestRef)
    orbitDao = OrbitDao()
    orbit = orbitDao.getOrbitWithTransaction(transaction, orbitRef)

    # TODO: validate that rideRequest is the same as when the decision is made to join rideRequest to orbit
    # TODO: validate that orbit is the same as when the decision is made to join rideRequest to orbit

    # Modify local copies of rideRequest and orbit
    placeInOrbit(rideRequest, orbit)

    # Update database copy of rideRequest and orbit
    try:
        rideRequestDao.setRideRequestWithTransaction(
            transaction, rideRequest, rideRequest.getFirestoreRef())
        orbitDao.setOrbitWithTransaction(
            transaction, orbit, orbit.getFirestoreRef())
        # TODO: add other works to be done if any
        transaction.commit()
    except:
        # Firestore rollsback operations automatically. No need for manual rollback.
       raise
