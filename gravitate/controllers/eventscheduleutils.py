from typing import Type

from gravitate.models import AirportEventSchedule, AirportRideRequest, Orbit, AirportLocation, ToEventTarget, Location, \
    RideRequest, SocialEventRideRequest, SocialEventLocation
from gravitate.data_access import UserDao
import warnings
from gravitate import context

CTX = context.Context


def _build_social_event_ride_request(event_schedule, event_ride_request: SocialEventRideRequest):
    event_schedule.pickupAddress = event_ride_request.pickup_address
    event_schedule.rideRequestRef = event_ride_request.get_firestore_ref()

    try:
        # Use destTime for sorting
        target: ToEventTarget = event_ride_request.target
        destTime = target.arrive_at_event_time["latest"]
        event_schedule.destTime = destTime
    except Exception as e:
        print(e)


def _build_airport_ride_request(event_schedule, airport_ride_request: AirportRideRequest):
    event_schedule.pickupAddress = airport_ride_request.pickup_address
    event_schedule.flightTime = airport_ride_request.flight_local_time
    event_schedule.rideRequestRef = airport_ride_request.get_firestore_ref()

    try:
        # Use destTime for sorting
        target: ToEventTarget = airport_ride_request.target
        destTime = target.arrive_at_event_time["latest"]
        event_schedule.destTime = destTime
    except Exception as e:
        print(e)


def _build_social_event_location(event_schedule, location: SocialEventLocation):

    event_schedule.destName = location.event_name  # Note that event name is not address
    event_schedule.locationRef = location.get_firestore_ref()


def _build_airport_location(event_schedule, location: AirportLocation):

    event_schedule.destName = location.airport_code
    event_schedule.locationRef = location.get_firestore_ref()


def _build_pending_orbit(event_schedule):
    event_schedule.memberProfilePhotoUrls = []
    event_schedule.pending = True
    event_schedule.orbitRef = None


def _build_orbit(event_schedule, orbit):
    event_schedule.pending = False
    event_schedule.memberProfilePhotoUrls = []
    # TODO implement and replace self.eventSchedule.memberProfilePhotoUrls = []
    event_schedule.memberProfilePhotoUrls = getMemberProfilePhotoUrls(orbit)
    event_schedule.orbitRef = orbit.get_firestore_ref()


class EventScheduleBuilder():

    def __init__(self, event_schedule: AirportEventSchedule = None):
        if event_schedule is None:
            self.event_schedule = AirportEventSchedule()
        else:
            self.event_schedule = event_schedule

    def build_ride_request(self, ride_request: Type[RideRequest]):
        if isinstance(ride_request, AirportRideRequest):
            _build_airport_ride_request(self.event_schedule, ride_request)
        elif isinstance(ride_request, SocialEventRideRequest):
            _build_social_event_ride_request(self.event_schedule, ride_request)
        else:
            raise NotImplementedError("Unsupported ride request type: {}".format(type(ride_request)))

    def build_location(self, location: Type[Location]):
        if isinstance(location, AirportLocation):
            _build_airport_location(self.event_schedule, location)
        elif isinstance(location, SocialEventLocation):
            _build_social_event_location(self.event_schedule, location)
        else:
            raise NotImplementedError("Unsupported location type: {}".format(type(location)))

    def build_orbit(self, pending=True, orbit: Orbit = None):
        if pending:
            _build_pending_orbit(self.event_schedule)
        else:
            _build_orbit(self.event_schedule, orbit)

    def export(self) -> AirportEventSchedule:
        return self.event_schedule


def create_event_schedule(ride_request: Type[RideRequest], location: Type[Location]):

    # Validate that type of location and type of ride request match
    if isinstance(ride_request, AirportRideRequest):
        assert isinstance(location, AirportLocation)
    elif isinstance(ride_request, SocialEventRideRequest):
        assert isinstance(location, SocialEventLocation)
    else:
        raise NotImplementedError("Unsupported ride request type: {}".format(type(ride_request)))

    event_schedule_builder = EventScheduleBuilder()
    event_schedule_builder.build_ride_request(ride_request)
    event_schedule_builder.build_location(location)  # Note that location=None defaults to LAX as destName
    event_schedule_builder.build_orbit(pending=True)
    return event_schedule_builder.export()


def create_event_schedule_orbit(ride_request: Type[RideRequest], location: Type[Location], orbit: Orbit):
    event_schedule_builder = EventScheduleBuilder()
    event_schedule_builder.build_ride_request(ride_request)
    event_schedule_builder.build_location(location)  # Note that location=None defaults to LAX as destName
    event_schedule_builder.build_orbit(pending=False, orbit=orbit)
    return event_schedule_builder.export()


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
    if CTX.testing:
        warnings.warn("Using testing mode, skipping member profile photo urls evaluation. ")
        return photo_urls

    for uid in orbit.user_ticket_pairs:
        user = UserDao().get_user_by_id(uid)
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
#         user = UserDao().get_user_by_id(uid)
#         photo_url = user.photo_url
#         photo_urls.append(photo_url)

#     return photo_urls
