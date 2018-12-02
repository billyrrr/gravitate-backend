from models.ride_request import RideRequest
from models.orbit import Orbit
# places RideRequest into the Orbit
# only works if orbit's orbitId, orbitCategory, and eventId is already instantiated


def placeInOrbit(r:RideRequest, o:Orbit) :
    # set RideRequest's requestCompletion to true
    r.requestCompletion = True

    # RideRequest's orbitId no longer null and references Orbit's oId
    r.orbitRef = getFirestoreRef(o) 

    # fill in ticket and insert in to orbit's userTicketPairs
    ticket = {"rideRequestId": r.rideRequestId, "userWillDrive": r.driverStatus,
              "hasCheckedIn": r.hasCheckedIn, "inChat": True, "pickupAdress": r.pickupAddress}
    o.userTicketPairs.append(ticket)

	# If an object passed in as parameter is modified, then return should, by convention, set to None. 
    return None

    # TODO: change the method to adapt to new RideRequest and Orbit object structure
    # TODO: change rideRequest.dictionary to rideRequest
