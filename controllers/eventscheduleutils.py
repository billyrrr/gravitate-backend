from models import EventSchedule, AirportRideRequest, Orbit, AirportLocation, ToEventTarget
from data_access import UserDao
import warnings
import google.cloud.firestore

class EventScheduleBuilder():

    def __init__(self, eventSchedule: EventSchedule=None):
        if not eventSchedule:
            self.eventSchedule = EventSchedule()
        else:
            self.eventSchedule = eventSchedule

    def buildRideRequest(self, airportRideRequest: AirportRideRequest):
        self.eventSchedule.pickupAddress = airportRideRequest.pickupAddress
        self.eventSchedule.flightTime = airportRideRequest.flightLocalTime
        self.eventSchedule.rideRequestRef = airportRideRequest.getFirestoreRef()

        # try:
        #     # Use destTime for sorting
        #     target: ToEventTarget = airportRideRequest.target
        #     destTime = target.arriveAtEventTime["latest"]
        #     self.eventSchedule.destTime = destTime
        # except Exception as e:
        #     print(e)

    def buildAirportLocation(self, location: AirportLocation):
        if not location:
            warnings.warn("LAX is hardcoded. Adapt to read from location object before release. ")
            self.eventSchedule.destName = "LAX"
            warnings.warn("locationRef is hardcoded. Adapt to read from location object before release. ")
            self.eventSchedule.locationRef = "/locations/AedTfnR2FhaLnVHriAMn"
        else:
            self.eventSchedule.destName = location.airportCode
            self.eventSchedule.locationRef = location.getFirestoreRef()
    
    def buildOrbit(self, pending = True, orbit: Orbit = None):
        if pending:
            self.eventSchedule.memberProfilePhotoUrls = []
            self.eventSchedule.pending = True
            self.eventSchedule.orbitRef = None
        else:
            self.eventSchedule.pending = False
            self.eventSchedule.memberProfilePhotoUrls = []
            # TODO implement and replace self.eventSchedule.memberProfilePhotoUrls = []
            self.eventSchedule.memberProfilePhotoUrls = getMemberProfilePhotoUrls(orbit)
            self.eventSchedule.orbitRef = orbit.getFirestoreRef()

    def export(self) -> EventSchedule:
        return self.eventSchedule


def buildEventSchedule(rideRequest: AirportRideRequest, location: AirportLocation = None):
    eventScheduleBuilder = EventScheduleBuilder()
    eventScheduleBuilder.buildRideRequest(rideRequest)
    eventScheduleBuilder.buildAirportLocation(location) # Note that location=None defaults to LAX as destName
    eventScheduleBuilder.buildOrbit(pending=True)
    eventSchedule = eventScheduleBuilder.export()
    return eventSchedule

def buildEventScheduleOrbit(rideRequest: AirportRideRequest, location: AirportLocation, orbit: Orbit):
    eventScheduleBuilder = EventScheduleBuilder()
    eventScheduleBuilder.buildRideRequest(rideRequest)
    eventScheduleBuilder.buildAirportLocation(location) # Note that location=None defaults to LAX as destName
    eventScheduleBuilder.buildOrbit(pending=False, orbit=orbit)
    eventSchedule = eventScheduleBuilder.export()
    return eventSchedule

def getMemberProfilePhotoUrls(orbit: Orbit) -> [str]:
    """ Description
        [Assigned to Leon]
        Don't have to follow the method signature, but the signature is required to get other code working. 
        Orbits can be obtained through any other ways, and buildEventSchedule can be called from elsewhere. 

    :raises:

    :rtype:
    """
    # Must go through each userTicketPair (key = userIDs)
    photo_urls = []
    for uid in orbit.userTicketPairs:
        user = UserDao().getUserById(uid)
        photo_url = user.photo_url
        photo_urls.append(photo_url)

    return photo_urls

    
# def populateMemberProfilePhotoUrls(ticketPairs:dict) -> [str]:    
#     """ Description
#         [Assigned to Leon]

#     :type userRefs:
#     :param userRefs:

#     :type userIds:
#     :param userIds:

#     :raises:

#     :rtype:
#     """
#     photo_urls = [];
#     for uid in ticketPairs:
#         user = UserDao().getUserById(uid)
#         photo_url = user.photo_url
#         photo_urls.append(photo_url)

#     return photo_urls
