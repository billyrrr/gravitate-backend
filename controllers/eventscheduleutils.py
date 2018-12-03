from models import EventSchedule, AirportRideRequest, Orbit, AirportLocation
import warnings
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
    
    def buildAirportLocation(self, location: AirportLocation):
        if not location:
            warnings.warn("LAX is hardcoded. Adapt to read from location object before release. ")
            self.destName = "LAX"
            warnings.warn("locationRef is hardcoded. Adapt to read from location object before release. ")
            self.locationRef = "/locations/AedTfnR2FhaLnVHriAMn"
        else:
            self.destName = location.airportCode
            self.locationRef = location.getFirestoreRef()
    
    def buildOrbit(self, pending = True, orbit: Orbit = None):
        if pending:
            self.pending = True
        else:
            self.pending = False
            raise NotImplementedError
            # Set memberProfilePhotoUrls
            # Set orbitId


def buildEventSchedule(rideRequest: AirportRideRequest, location: AirportLocation = None):
    eventSchedule = EventScheduleBuilder()
    eventSchedule.buildRideRequest(rideRequest)
    eventSchedule.buildAirportLocation(location) # Note that location=None defaults to LAX as destName
    eventSchedule.buildNoOrbit()
    return eventSchedule

def populateMemberProfiles(userRefs=None, userIds=None) -> [str]:
    raise NotImplementedError()