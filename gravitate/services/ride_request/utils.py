from typing import Type

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
    target = utils.createTargetWithFlightLocalTime(form.flightLocalTime, form.toEvent)
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
    b: AirportRideRequestBuilder = AirportRideRequestBuilder().set_user(userId).set_flight(flight_local_time=form.flightLocalTime, flight_number=form.flightNumber).set_location(airport_code=form.airportCode).set_time(flight_local_time=form.flightLocalTime, to_event=form.toEvent).build_airport_ride_request()
    return b.ride_request_dict, utils.getAirportLocation(form.airportCode)


class RideRequestBaseBuilder:

    def __init__(self):
        self.ride_request_dict = dict()

    def export_as_class(self, export_class) -> Type[RideRequest]:
        return export_class.from_dict(self.ride_request_dict)


class AirportRideRequestBuilder(RideRequestBaseBuilder):
    """
    Note that this class is not following any design pattern at all. It should be thoroughly tested before use.
        "var if var is not None else self.var"
            prevents a variable already set from being overridden by None.

        TODO: test and finish implementing
    """

    user_id = None
    location_id = None
    airport_code = None
    earliest = None
    latest = None
    to_event = None
    flight_local_time = None
    flight_number = None
    eventRef = None

    def set_user(self, user_id):
        self.user_id = user_id
        return self

    def _build_user(self):
        if self.user_id is not None:
            self.ride_request_dict["userId"] = self.user_id
        else:
            raise ValueError("user_id is not set ")

    def set_flight(self, flight_local_time=None, flight_number=None):
        self.flight_local_time = flight_local_time if flight_local_time is not None else self.flight_local_time
        self.flight_number = flight_number if flight_number is not None else self.flight_number
        return self

    def _build_flight(self):
        self.ride_request_dict["flightLocalTime"] = self.flight_local_time
        self.ride_request_dict["flightNumber"] = self.flight_number

    def set_location(self, location_id=None, airport_code=None):
        if location_id is not None:
            self.location_id = location_id
        elif airport_code is not None:
            self.airport_code = airport_code
        else:
            raise ValueError
        return self

    def set_time(self, earliest=None, latest=None, to_event: bool=None, flight_local_time=None):
        self.earliest = earliest if earliest is not None else self.earliest
        self.latest = latest if latest is not None else self.latest
        self.to_event = to_event if to_event is not None else self.to_event
        self.flight_local_time = flight_local_time if flight_local_time else self.flight_local_time
        return self

    def build_airport_ride_request(self):
        self._build_flight()
        self._build_user()
        self._build_location()
        self._build_target_and_time()
        self._build_event()
        self._build_disabilities()
        self._build_baggages()
        self._build_ride_request_default_values()
        return self

    def _build_location(self):
        # Note that the key is airportLocation rather than locationRef TODO: change model
        if self.airport_code is not None:
            self.ride_request_dict["airportLocation"] = self._get_location_ref(self.airport_code)
        elif self.location_id is not None:
            self.ride_request_dict["airportLocation"] = utils.get_location_ref_by_id(self.location_id)
        else:
            raise ValueError

    @staticmethod
    def _get_location_ref(airport_code):
        location = utils.getAirportLocation(airport_code)
        return location.get_firestore_ref()

    def _build_target_and_time(self):
        assert self.to_event is not None
        if self.earliest is not None and self.latest is not None:
            target = Target.create_airport_event_target(self.to_event, self.earliest, self.latest)
            self.ride_request_dict["target"] = target.to_dict()
        elif self.flight_local_time is not None:
            target = utils.createTargetWithFlightLocalTime(self.flight_local_time, self.to_event)
            self.ride_request_dict["target"] = target.to_dict()
        else:
            raise TypeError

    def _build_event(self):
        if self.eventRef is None:
            self.ride_request_dict["eventRef"] = utils.findEvent(self.flight_local_time)
        else:
            self.ride_request_dict["eventRef"] = self.eventRef

    def _build_disabilities(self):
        self.ride_request_dict["disabilities"] = dict()

    def _build_baggages(self):
        self.ride_request_dict["baggages"] = dict()

    def _build_ride_request_default_values(self):
        self.ride_request_dict["requestCompletion"] = False
        self.ride_request_dict["orbitRef"] = None
        self.ride_request_dict["driverStatus"] = False
        self.ride_request_dict['hasCheckedIn'] = False



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
    target = utils.createTargetWithFlightLocalTime(d["flightLocalTime"], toEvent)
    d['target'] = target.to_dict()

    if "eventId" in form.keys() and "locationId" in form.keys():
        d['eventRef'] = utils.get_event_ref_by_id(form["eventId"])
        d['airportLocation'] = utils.get_location_ref_by_id(form["locationId"])
    else:
        location = utils.getAirportLocation(form["airportCode"])
        if not location:
            raise ValueError("AirportLocation cannot be found with airportCode provided. ")  # TODO: error handling: https://stackoverflow.com/questions/21294889/how-to-get-access-to-error-message-from-abort-command-when-using-custom-error-ha/21297608

    # Set EventRef
    event_ref = utils.findEvent(d["flightLocalTime"])
    d['eventRef'] = event_ref

    airport_location_ref = location.get_firestore_ref()
    d['airportLocation'] = airport_location_ref

    ride_request = utils.get_ride_request(d)

    return ride_request
