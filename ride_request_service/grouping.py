from ride_request_service.associate_ride_request_with_orbit import joinOrbitToRideRequest
from models.orbit import Orbit
from google.cloud.firestore import Client

client = Client()

def groupRideRequests():
    
    
    """ Description
        [Not Implemented]
        This function 
        1. reads all ride requests associated with an event
        2. puts ride requests into groups
        3. call join method on each group
    :raises:

    :rtype:
    """
    
    # TODO Implement

    pass

class Group:

    def __init__(self, rideRequestArray:[]):
        self.rideRequestArray = rideRequestArray

        # Note that the intended orbit will be in database, and hence possible to be modified by another thread
        self.intendedOrbit = None # TODO create an orbit (may need a factory pattern) and add to database

    def doWork(self):
        orbit = self.intendedOrbit

        # Record which users failed join the orbit
        notJoined = []

        for rideRequest in self.rideRequestArray:
            try:
                # Trying to join one rideRequest to the orbit
                joinOrbitToRideRequest(client, rideRequest.firestoreRef, rideRequest, orbit.firestoreRef, orbit)
            except:
                # TODO when failing to join, move on to next
                notJoined.append(rideRequest)
                raise

        return notJoined
        