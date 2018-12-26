import warnings
from typing import Type

import gravitate.models.target
from gravitate.controllers import utils
from gravitate.forms.ride_request_creation_form import AirportRideRequestCreationForm
from gravitate.models import AirportLocation, RideRequest, Target


def fill_ride_request_dict_with_form(form: AirportRideRequestCreationForm, userId) -> (dict, AirportLocation):
    """ Description
        This method fills a rideRequest dict that can later be used to call RideRequest().from_dict method.
    :param form:
    :param userId:
    :return: a tuple of rideRequest dict and AirportLocation
    """
    rideRequestDict = dict()

    rideRequestDict['rideCategory'] = 'airportRide'

    # Move data from the form frontend submitted to rideRequestDict
    rideRequestDict['pickupAddress'] = form.pickupAddress
    rideRequestDict['driverStatus'] = form.driverStatus
    rideRequestDict['flightLocalTime'] = form.flightLocalTime
    rideRequestDict['flightNumber'] = form.flightNumber

    # Fields to be filled "immediately"

    # TODO fill unspecified options with default values
    rideRequestDict['pricing'] = 987654321  # TODO change

    # Populate rideRequestDict with default service data
    rideRequestDict['disabilities'] = dict()
    rideRequestDict['baggages'] = dict()
    rideRequestDict['hasCheckedIn'] = False
    rideRequestDict['orbitRef'] = None
    rideRequestDict['userId'] = userId
    rideRequestDict['requestCompletion'] = False

    # Fields to be filled "after some thinking"

    # Set Target
    target = Target.create_with_flight_local_time(form.flightLocalTime, form.toEvent)
    rideRequestDict['target'] = target.to_dict()

    # Set EventRef
    eventRef = utils.findEvent(form.flightLocalTime)
    rideRequestDict['eventRef'] = eventRef
    location = utils.getAirportLocation(form.airportCode)
    if not location:
        return rideRequestDict, None
    airportLocationRef = location.get_firestore_ref()
    rideRequestDict['airportLocation'] = airportLocationRef

    return rideRequestDict, location


def fill_ride_request_dict_builder_regression(form: AirportRideRequestCreationForm, userId) -> (dict, AirportLocation):
    """
    Adaptor pattern for testing purposes only
    :param form:
    :param userId:
    :return:
    """
    warnings.warn("This method is for testing purposes only. Do not use in production. ")
    f: dict = vars(form)
    b: AirportRideRequestBuilder = AirportRideRequestBuilder().set_with_form_and_user_id(f, userId)\
        .build_airport_ride_request()
    return b._ride_request_dict, utils.getAirportLocation(form.airportCode)


class RideRequestBaseBuilder:

    def __init__(self):
        self._ride_request_dict = dict()

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

    _ride_request_dict = None

    user_id = None
    location_id = None
    airport_code = None
    earliest = None
    latest = None
    to_event = None
    flight_local_time = None
    flight_number = None
    eventRef = None
    pickup_address = None
    pricing = None
    driver_status = None

    def set_data(self, user_id=None, flight_local_time=None, flight_number=None, earliest=None, latest=None,
                 to_event: bool = None, location_id=None, airport_code=None, pickup_address=None, pricing=None,
                 driver_status: bool = None):
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

    @staticmethod
    def _get_location_ref(airport_code):
        location = utils.getAirportLocation(airport_code)
        return location.get_firestore_ref()

    def _build_target_earliest_latest(self):
        target = Target.create_airport_event_target(self.to_event, self.earliest, self.latest)
        self._ride_request_dict["target"] = target.to_dict()

    def _build_target_with_flight_local_time(self):
        target = Target.create_with_flight_local_time(self.flight_local_time, self.to_event)
        self._ride_request_dict["target"] = target.to_dict()

    def _build_event_with_flight_local_time(self):
        self._ride_request_dict["eventRef"] = utils.findEvent(self.flight_local_time)

    def _build_event_with_id(self):
        """
        TODO: change to event id
        :return:
        """
        self._ride_request_dict["eventRef"] = self.eventRef

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
        self._build_event_with_flight_local_time()
        self._build_disabilities()
        self._build_baggages()
        self._build_ride_request_default_values()
        self._build_ride_category()
        self._build_pickup()
        return self


class CampusEventRideRequestBuilder(RideRequestBaseBuilder):

    def __init__(self):
        super().__init__()


def create_ride_request(form: dict, user_id: str) -> Type[RideRequest]:
    """ Description
        This method creates a rideRequest from form of type:
            FL-3: flightNumber, flightLocalTime, airportCode, ...
            ... other use cases
        TODO: move to builder pattern

    :param form:
    :param user_id:
    :return: rideRequest
    """

    raise NotImplementedError

    d = dict()

    d['rideCategory'] = 'airportRide'
    toEvent = form["toEvent"]

    # Move data from the form frontend submitted to rideRequestDict
    if "pickupAddress" in form.keys():
        d['pickupAddress'] = form["pickupAddress"]
    else:
        d['pickupAddress'] = utils.getPickupAddress(user_id)
    d['driverStatus'] = form["driverStatus"]
    d['flightLocalTime'] = form["flightLocalTime"]
    d['flightNumber'] = form["flightNumber"]

    # Fields to be filled "immediately"

    # TODO fill unspecified options with default values
    d['pricing'] = 987654321  # TODO change

    # Populate rideRequestDict with default service data
    d['disabilities'] = dict()
    d['baggages'] = dict()
    d['hasCheckedIn'] = False
    d['orbitRef'] = None
    d['userId'] = user_id
    d['requestCompletion'] = False

    # Fields to be filled "after some thinking"

    # Set Target
    target = Target.create_with_flight_local_time(d["flightLocalTime"], toEvent)
    d['target'] = target.to_dict()

    if "eventId" in form.keys() and "locationId" in form.keys():
        d['eventRef'] = utils.get_event_ref_by_id(form["eventId"])
        d['airportLocation'] = utils.get_location_ref_by_id(form["locationId"])
    else:
        location = utils.getAirportLocation(form["airportCode"])
        if not location:
            raise ValueError(
                "AirportLocation cannot be found with airportCode provided. ")  # TODO: error handling: https://stackoverflow.com/questions/21294889/how-to-get-access-to-error-message-from-abort-command-when-using-custom-error-ha/21297608

    # Set EventRef
    event_ref = utils.findEvent(d["flightLocalTime"])
    d['eventRef'] = event_ref

    airport_location_ref = location.get_firestore_ref()
    d['airportLocation'] = airport_location_ref

    ride_request = utils.get_ride_request(d)

    return ride_request
