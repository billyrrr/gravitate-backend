from gravitate.controllers import utils
from gravitate.forms.ride_request_creation_form import AirportRideRequestCreationForm
from gravitate.models import AirportLocation


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