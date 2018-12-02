from models.ride_request import RideRequest
from models.orbit import Orbit
# places RideRequest into the Orbit
# only works if orbit's orbitId, orbitCategory, and eventId is already instantiated


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
