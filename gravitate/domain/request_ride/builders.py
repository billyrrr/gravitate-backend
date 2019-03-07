from typing import Type

from gravitate.domain.request_ride import utils
from gravitate.models import RideRequest, Target
from gravitate.data_access import EventDao


class RideRequestBaseBuilder:

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

    """
        Note that this class is not following any design pattern at all. It should be thoroughly tested before use.
            "var if var is not None else self.var"
                prevents a variable already set from being overridden by None.

            TODO: test and finish implementing
        """

    def set_data(self, user_id=None, flight_local_time=None, flight_number=None, earliest=None, latest=None,
                 to_event: bool = None, location_id=None, airport_code=None, pickup_address=None, pricing=None,
                 driver_status: bool = None, event_id=None):
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

    def _build_user(self):
        if self.user_id is not None:
            self._ride_request_dict["userId"] = self.user_id
        else:
            raise ValueError("user_id is not set ")

    def _build_flight(self):
        self._ride_request_dict["flightLocalTime"] = self.flight_local_time
        self._ride_request_dict["flightNumber"] = self.flight_number

    def _build_location_by_airport_code(self):
        # Note that the key is airportLocation rather than locationRef TODO: change model
        self._ride_request_dict["airportLocation"] = self._get_location_ref(self.airport_code)

    def _build_location_by_id(self):
        self._ride_request_dict["airportLocation"] = utils.get_location_ref_by_id(self.location_id)

    def _build_location_by_event(self):
        print(self.event.to_dict())
        self._ride_request_dict["locationRef"] = self.event.location_ref

    @staticmethod
    def _get_location_ref(airport_code):
        location = utils.get_airport_location(airport_code)
        return location.get_firestore_ref()

    def _build_target_earliest_latest(self):
        target = Target.create_airport_event_target(self.to_event, self.earliest, self.latest)
        self._ride_request_dict["target"] = target.to_dict()

    def _build_target_anytime(self):
        earliest = self.event.start_timestamp
        latest = self.event.end_timestamp
        target = Target.create_social_event_target(self.to_event, earliest, latest)
        self._ride_request_dict["target"] = target.to_dict()

    def _build_target_with_flight_local_time(self):
        target = Target.create_with_flight_local_time(self.flight_local_time, self.to_event)
        self._ride_request_dict["target"] = target.to_dict()

    def _build_event_ref_with_flight_local_time(self):
        self._ride_request_dict["eventRef"] = utils.find_event(self.flight_local_time)

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

    def _build_ride_category(self):
        """
        To be overridden by subclass
        :return:
        """
        raise NotImplementedError("This is an abstract method. Override it in subclass. ")

    def _build_pickup(self):
        self._ride_request_dict["pickupAddress"] = self.pickup_address


class AirportRideRequestBuilder(RideRequestBaseBuilder):

    def set_with_form_and_user_id(self, d, user_id):
        """
        TODO: parse all fields from form. None if does not exist
        :param d:
        :param user_id:
        :return:
        """
        self.user_id = user_id
        self.set_data(
            user_id=user_id, flight_local_time=d["flightLocalTime"], flight_number=d["flightNumber"],
            airport_code=d["airportCode"], to_event=d["toEvent"], pickup_address=d["pickupAddress"],
            driver_status=d["driverStatus"]
        )
        return self

    def _build_ride_category(self):
        self._ride_request_dict["rideCategory"] = "airportRide"

    def build_airport_ride_request(self):
        assert self.flight_local_time is not None
        assert self.earliest is None and self.latest is None  # They will be overridden by those of flightLocalTime

        self._build_flight()
        self._build_user()
        self._build_location_by_airport_code()  # Use airportCode to infer location
        self._build_target_with_flight_local_time()  # Use flightLocalTime to build target
        self._build_event_ref_with_flight_local_time()
        self._build_disabilities()
        self._build_baggages()
        self._build_ride_request_default_values()
        self._build_ride_category()
        self._build_pickup()
        return self


class SocialEventRideRequestBuilder(RideRequestBaseBuilder):

    def _build_ride_category(self):
        self._ride_request_dict["rideCategory"] = "eventRide"

    def set_with_form_and_user_id(self, d, user_id):
        """
        TODO: parse all fields from form. None if does not exist
        :param d:
        :param user_id:
        :return:
        """
        self.user_id = user_id
        self.set_data(
            user_id=user_id, event_id=d["eventId"],
            to_event=d["toEvent"], pickup_address=d["pickupAddress"],
            driver_status=d["driverStatus"]
        )
        return self

    def build_social_event_ride_request(self):

        self._build_ride_category()

        self._build_user()

        self._build_event_with_id()

        self._build_target_anytime()

        self._build_location_by_event()

        self._build_event_ref_with_event()

        self._build_disabilities()
        self._build_baggages()

        self._build_pickup()

        self._build_ride_request_default_values()

        return self


class CampusEventRideRequestBuilder(RideRequestBaseBuilder):

    def __init__(self):
        super().__init__()

