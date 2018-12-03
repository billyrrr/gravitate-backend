from models import EventSchedule, AirportRideRequest, Orbit

class EventScheduleBuilder(EventSchedule):

    def __init__(self):
        super().__init__()

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
    # eventScheduleDict = {
    #     "destName": "",
    #     "destTime": "",
    #     "flightTime": "",
    #     "memberProfilePhotoUrls": [],
    #     "pickupAddress": "",
    #     "pending": None
    # }
    eventSchedule = EventScheduleBuilder()
    eventSchedule.buildRideRequest(rideRequest)
    return eventSchedule

