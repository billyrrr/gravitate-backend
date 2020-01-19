from typing import Type

from gravitate.domain.event.dao import EventDao
from . import utils
from . import RideRequest
from gravitate.domain.location.models import Location, LocationFactory
from gravitate.models import Target


class RideRequestBaseBuilder:
    """
    Builder for RideRequest. This class simplifies the workflow for creating ride request.
    Usage:
        1. Instantiate <AirportRideRequestBuilder|SocialEventRideRequestBuilder>
        2. Call .set_data or .set_with_form_and_user_id if calling from REST API layer
        3. Call .export_as_class(<AirportRideRequest|SocialEventRideRequest>)

    """

    ride_category = None

    def __init__(self):
        self._ride_request_dict = dict()
        # _ride_request_dict = None

        self.user_id = None
        self.location_id = None
        self.airport_code = None
        self.earliest = None
        self.latest = None
        self.to_event = None
        self.flight_local_time = None
        self.flight_number = None
        self.eventRef = None
        self.pickup_address = None
        self.pricing = None
        self.driver_status = None

        self.event_id = None

        # Helper data
        self.event = None

    def export_as_class(self, export_class) -> Type[RideRequest]:
        """
        :param: export_class: the class to call .from_dict with
        Note that export_class=AirportRideRequest and export_class=RideRequest yield the same result,
            since AirportRideRequest.from_dict is the same as RideRequest.from_dict.
        """
        return export_class.from_dict(self._ride_request_dict)

    def set_data(self, user_id=None, flight_local_time=None, flight_number=None, earliest=None, latest=None,
                 to_event: bool = None, location_id=None, airport_code=None, pickup_address=None, pricing=None,
                 driver_status: bool = None, event_id=None):
        """
        Sets data that may be used by the builder
        :param user_id:
        :param flight_local_time:
        :param flight_number:
        :param earliest:
        :param latest:
        :param to_event:
        :param location_id:
        :param airport_code:
        :param pickup_address:
        :param pricing:
        :param driver_status:
        :param event_id:
        :return:
        """
        self.user_id = user_id
        self.flight_local_time = flight_local_time
        self.flight_number = flight_number

        self.earliest = earliest
        self.latest = latest
        self.to_event = to_event
        self.location_id = location_id
        self.airport_code = airport_code

        self.pickup_address = pickup_address
        self.pricing = pricing

        self.to_event = to_event
        self.driver_status = driver_status

        self.event_id = event_id

        return self

    def _build_ride_category(self):
        self._ride_request_dict["rideCategory"] = self.ride_category

    def _build_user(self):
        if self.user_id is not None:
            self._ride_request_dict["userId"] = self.user_id
        else:
            raise ValueError("user_id is not set ")

    def _build_flight(self):
        self._ride_request_dict["flightLocalTime"] = self.flight_local_time
        self._ride_request_dict["flightNumber"] = self.flight_number

    def _build_location_by_airport_code(self):
        self._ride_request_dict["airportLocation"] = self._get_location_ref(self.airport_code)
        self._ride_request_dict["destinationRef"] = self._get_location_ref(self.airport_code)

    def _build_location_by_id(self):
        self._ride_request_dict["destinationRef"] = utils.get_location_ref_by_id(self.location_id)

    def _build_location_by_event(self):
        # print(self.event.to_dict())
        self._ride_request_dict["locationRef"] = self.event.location_ref
        self._ride_request_dict["destinationRef"] = self.event.location_ref

    @staticmethod
    def _get_location_ref(airport_code):
        location = utils.get_airport_location(airport_code)
        return location.get_firestore_ref()

    def _build_target_earliest_latest(self):
        # TODO: Change back
        target = Target.create_with_local_time_str(self.to_event, self.earliest, self.latest, self.ride_category)
        self._ride_request_dict["target"] = target.to_dict()

    def _build_target_anytime(self):
        earliest = self.event.start_timestamp
        latest = self.event.end_timestamp
        target = Target.create_social_event_target(self.to_event, earliest, latest)
        self._ride_request_dict["target"] = target.to_dict()

    def _build_target_with_event_target(self):
        for target in self.event.targets:
            if target.to_event == self.to_event:
                self._ride_request_dict["target"] = target.to_dict()

    def _build_target_with_flight_local_time(self):
        target = Target.create_with_flight_local_time(self.flight_local_time, self.to_event)
        self._ride_request_dict["target"] = target.to_dict()

    def _build_event_ref_with_flight_local_time(self):
        print("-------------")
        self._ride_request_dict["eventRef"] = utils.find_event(self.flight_local_time)
        print(utils.find_event(self.flight_local_time))

    def _build_event_with_id(self):
        """
        TODO: change to event id
        :return:
        """

        event = EventDao().get_by_id(self.event_id)
        self.event = event

    def _build_event_ref_with_event(self):
        self._ride_request_dict["eventRef"] = self.event.get_firestore_ref()

    def _build_disabilities(self):
        self._ride_request_dict["disabilities"] = dict()

    def _build_baggages(self):
        self._ride_request_dict["baggages"] = dict()

    def _build_ride_request_default_values(self):
        self._ride_request_dict["requestCompletion"] = False
        self._ride_request_dict["orbitRef"] = None
        self._ride_request_dict["driverStatus"] = False
        self._ride_request_dict['hasCheckedIn'] = False
        self._ride_request_dict['pricing'] = 987654321

    def _build_pickup(self):
        origin_location = LocationFactory.from_pickup_address(
            pickup_address=self.pickup_address)
        origin_location.save()
        origin_ref = origin_location.doc_ref
        self._ride_request_dict["originRef"] = origin_ref
        # self._ride_request_dict["pickupAddress"] = self.pickup_address

    def earliest_latest_specified(self):
        if self.earliest is None and self.latest is None:
            return False
        elif self.earliest is not None and self.latest is not None:
            return True
        else:
            raise ValueError


class AirportRideRequestBuilder(RideRequestBaseBuilder):

    ride_category = "airportRide"

    def set_with_form_and_user_id(self, d, user_id):
        """ Save arguments as instance variables in builder

        :param d: argument dict returned by .parse_args() from a reqparse object
        :param user_id: user id
        :return: AirportRideRequestBuilder
        """
        self.user_id = user_id
        self.set_data(
            user_id=user_id, flight_local_time=d.get("flightLocalTime", None), flight_number=d["flightNumber"],
            airport_code=d["airportCode"], to_event=d["toEvent"], pickup_address=d["pickupAddress"],
            driver_status=d["driverStatus"], earliest=d.get("earliest", None), latest=d.get("latest", None)
        )
        return self

    def flight_local_time_specified(self):
        return self.flight_local_time is not None

    def build_airport_ride_request(self):

        if self.earliest_latest_specified():
            # Use specified earliest and latest by default
            self._build_target_earliest_latest()
        elif self.flight_local_time_specified():
            # Earliest and latest will be overridden by those of flightLocalTime
            self._build_target_with_flight_local_time()
        else:
            # Must have one or the other
            raise ValueError

        self._build_flight()
        self._build_user()
        self._build_location_by_airport_code()  # Use airportCode to infer location
        self._build_event_ref_with_flight_local_time()
        self._build_disabilities()
        self._build_baggages()
        self._build_ride_request_default_values()
        self._build_ride_category()
        self._build_pickup()
        return self


class SocialEventRideRequestBuilder(RideRequestBaseBuilder):

    ride_category = "eventRide"

    def set_with_form_and_user_id(self, d, user_id):
        """ Save arguments as instance variables in builder

        :param d:
        :param user_id:
        :return: SocialEventRideRequestBuilder
        """
        self.user_id = user_id
        self.set_data(
            user_id=user_id, event_id=d["eventId"],
            to_event=d["toEvent"], pickup_address=d["pickupAddress"],
            driver_status=d["driverStatus"], earliest=d.get("earliest", None), latest=d.get("latest", None)
        )
        return self

    def build_social_event_ride_request(self):
        """ Builds SocialEventRideRequest from instance variables
        :return:
        """
        self._build_ride_category()
        self._build_user()
        self._build_event_with_id()

        if self.earliest_latest_specified():
            self._build_target_earliest_latest()
        else:
            self._build_target_with_event_target()

        self._build_location_by_event()
        self._build_event_ref_with_event()
        self._build_disabilities()
        self._build_baggages()
        self._build_pickup()
        self._build_ride_request_default_values()

        return self


class CampusEventRideRequestBuilder(RideRequestBaseBuilder):
    """
    TODO: implement
    """
    pass
