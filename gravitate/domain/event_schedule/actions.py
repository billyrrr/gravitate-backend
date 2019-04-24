from typing import Type

from gravitate.domain.event_schedule.builders import EventScheduleBuilder
from gravitate.domain.rides import RideRequest, AirportRideRequest, SocialEventRideRequest
from gravitate.domain.location.models import Location, AirportLocation, SocialEventLocation
from gravitate.models import Orbit


def create_event_schedule(ride_request: Type[RideRequest], location: Type[Location], event=None):

    # Validate that type of location and type of ride request match
    if isinstance(ride_request, AirportRideRequest):
        assert isinstance(location, AirportLocation)
    elif isinstance(ride_request, SocialEventRideRequest):
        assert isinstance(location, SocialEventLocation)
        assert event is not None
    else:
        raise NotImplementedError("Unsupported ride request type: {}".format(type(ride_request)))

    event_schedule_builder = EventScheduleBuilder()
    event_schedule_builder.build_ride_request(ride_request)
    event_schedule_builder.build_event(event)
    event_schedule_builder.build_location(location)  # Note that location=None defaults to LAX as destName
    # event_schedule_builder.build_user_location(user_location)
    event_schedule_builder.build_orbit(pending=True)
    print(event_schedule_builder.event_schedule.to_dict())
    return event_schedule_builder.export()


def create_event_schedule_orbit(ride_request: Type[RideRequest], location: Type[Location], orbit: Orbit):
    event_schedule_builder = EventScheduleBuilder()
    event_schedule_builder.build_ride_request(ride_request)
    event_schedule_builder.build_location(location)  # Note that location=None defaults to LAX as destName
    event_schedule_builder.build_orbit(pending=False, orbit=orbit)
    return event_schedule_builder.export()
