from typing import Type

from gravitate.domain.event_schedule.utils import getMemberProfilePhotoUrls
from gravitate.domain.rides import SocialEventRideRequest, AirportRideRequest, RideRequest
from gravitate.models import ToEventTarget, SocialEventLocation, \
    AirportLocation, Location, Orbit
from gravitate.domain.event_schedule import AirportEventSchedule
from gravitate.models.location import UserLocation


def _build_social_event_ride_request(event_schedule, event_ride_request: SocialEventRideRequest):
    event_schedule.pickupAddress = event_ride_request.pickup_address
    event_schedule.rideRequestRef = event_ride_request.get_firestore_ref()
    event_schedule.toEvent = event_ride_request.target.to_event

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
    event_schedule.toEvent = airport_ride_request.target.to_event

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


def _build_user_location(event_schedule, location: UserLocation):
    event_schedule.pickupAddress = location.address


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


def _build_facebook_event_id(event_schedule, event):
    event_schedule.fbEventId = event.fb_event_id


class EventScheduleBuilder:

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

    def build_event(self, event):
        if event is not None:
            _build_facebook_event_id(self.event_schedule, event)

    def build_location(self, location: Type[Location]):
        if isinstance(location, AirportLocation):
            _build_airport_location(self.event_schedule, location)
        elif isinstance(location, SocialEventLocation):
            _build_social_event_location(self.event_schedule, location)
        else:
            raise NotImplementedError("Unsupported location type: {}".format(type(location)))

    def build_user_location(self, location: UserLocation):
        _build_user_location(self.event_schedule, location)

    def build_orbit(self, pending=True, orbit: Orbit = None):
        if pending:
            _build_pending_orbit(self.event_schedule)
        else:
            _build_orbit(self.event_schedule, orbit)

    def export(self) -> AirportEventSchedule:
        return self.event_schedule
