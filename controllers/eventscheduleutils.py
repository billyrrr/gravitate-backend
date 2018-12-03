from models import EventSchedule, AirportRideRequest, Orbit
import google.cloud.firestore

class EventScheduleBuilder(EventSchedule):

    def __init__(self):
        super().__init__()

    def buildNoOrbit(self):
        self.memberProfilePhotoUrls = []
        self.pending = True

    def buildRideRequest(self, airportRideRequest: AirportRideRequest):
        self.pickupAddress = airportRideRequest.pickupAddress
        self.flightTime = airportRideRequest.flightLocalTime
        self.rideRequestRef = airportRideRequest.getFirestoreRef()

    
    def buildOrbit(self, pending = True, orbit: Orbit = None):
        if pending:
            self.pending = True
        else:
            self.pending = False
            raise NotImplementedError
            # Set memberProfilePhotoUrls
            # Set orbitId


def buildEventSchedule(rideRequest: AirportRideRequest):
    eventSchedule = EventScheduleBuilder()
    eventSchedule.buildRideRequest(rideRequest)
    eventSchedule.buildNoOrbit()
    return eventSchedule

def populateMemberProfiles(userRefs=None, userIds=None) -> [str]:
    raise NotImplementedError()