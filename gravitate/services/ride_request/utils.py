from gravitate.controllers import utils
from gravitate.forms.ride_request_creation_form import AirportRideRequestCreationForm
from gravitate.models import AirportLocation, RideRequest


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


def create_ride_request(form: dict, user_id: str) -> type[RideRequest]:
    """ Description
        This method creates a rideRequest from form of type:
            FL-3: flightNumber, flightLocalTime, airportCode, ...
            ... other use cases

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
