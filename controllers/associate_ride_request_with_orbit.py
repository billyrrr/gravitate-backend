from models.orbit import Orbit
from models.ride_request import RideRequest
from data_access.ride_request_dao import RideRequestDao
from data_access.orbit_dao import OrbitDao
from google.cloud.firestore import *
from usersHelper.placeInOrbit import placeInOrbit

def joinOrbitToRideRequest(client: Client, rideRequestRef: DocumentReference, orbitRef: DocumentReference):

    # Create a transaction so that an exception is thrown when updating an object that is changed since last read from database
    transaction = client.transaction()


    rideRequestDao = RideRequestDao(client)
    rideRequest = rideRequestDao.getRideRequestWithTransaction(transaction, rideRequestRef)
    orbitDao = OrbitDao(client)
    orbit = orbitDao.getOrbitWithTransaction(transaction, orbitRef)

    # TODO: validate that rideRequest is the same as when the decision is made to join rideRequest to orbit
    # TODO: validate that orbit is the same as when the decision is made to join rideRequest to orbit

    # Modify local copies of rideRequest and orbit
    placeInOrbit(rideRequest, orbit)

    # Update database copy of rideRequest and orbit
    try: 
        rideRequestDao.setRideRequestWithTransaction(transaction, rideRequest, rideRequest.firestoreRef)
        orbitDao.setOrbitWithTransaction(transaction, orbit, orbit.firestoreRef)
        # TODO: add other works to be done if any
        transaction.commit()
    except:
        # Firestore rollsback operations automatically. No need for manual rollback. 
        raise
