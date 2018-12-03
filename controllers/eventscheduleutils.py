from models import EventSchedule, AirportRideRequest, Orbit

class EventSchedulerBuilder(EventSchedule):

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


def createEventSchedule():
    eventScheduleDict = {
        "destName": "",
        "destTime": "",
        "flightTime": "",
        "memberProfilePhotoUrls": [],
        "pickupAddress": "",
        "pending": None
    }