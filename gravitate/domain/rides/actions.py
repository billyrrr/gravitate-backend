from gravitate import context
from gravitate.api_server import errors as service_errors
from gravitate.domain.event.dao import EventDao
from gravitate.domain.location import Location
from .builders import AirportRideRequestBuilder, SocialEventRideRequestBuilder
from . import utils
from . import AirportRideRequest, SocialEventRideRequest

db = context.Context.db


def create(args, user_id, ride_category="airport"):
    """ Creates a ride request with arguments received by REST API endpoint

    :param args: argument dict returned by .parse_args() from a reqparse object
    :param user_id: user id
    :param ride_category: "airport" | "event"
    :return: RideRequest object
    """
    if ride_category == "airport":
        return _create_airport_ride_request(args, user_id)
    elif ride_category == "event":
        return _create_social_event_ride_request(args, user_id)
    else:
        raise ValueError("ride_category not supported: {}".format(ride_category))


def _create_airport_ride_request(args, user_id):
    """ Creates an airport ride request with arguments received by REST API endpoint

    :param args: argument dict returned by .parse_args() from a reqparse object
    :param user_id: user id
    :return: RideRequest object
    """
    builder = AirportRideRequestBuilder()
    ride_request: AirportRideRequest = builder \
        .set_with_form_and_user_id(args, user_id) \
        .build_airport_ride_request() \
        .export_as_class(AirportRideRequest)
    location = Location.get(ride_request.airport_location)
    if ride_request.target.to_event:
        user_location = Location.get(ride_request.origin_ref)
    else:
        raise ValueError("to_event is False ")
    # Do Validation Tasks before saving rideRequest
    # 1. Check that rideRequest is not submitted by the same user
    #       for the flight on the same day already
    # TODO: move to transactional logic for better atomicity
    if utils.check_duplicate(ride_request.user_id, ride_request.event_ref):
        raise service_errors.RequestAlreadyExistsError
    # Starts database operations to (save rideRequest and update user's eventSchedule)
    transaction = db.transaction()
    # Transactional business logic for adding rideRequest
    utils.add_ride_request(transaction, ride_request, location, user_id)
    # Save write result
    transaction.commit()
    return ride_request


def _create_social_event_ride_request(args, user_id):
    """ Creates an social event ride request with arguments received by REST API endpoint

    :param args: argument dict returned by .parse_args() from a reqparse object
    :param user_id: user id
    :return: RideRequest object
    """
    builder = SocialEventRideRequestBuilder()
    ride_request: SocialEventRideRequest = builder \
        .set_with_form_and_user_id(args, user_id) \
        .build_social_event_ride_request() \
        .export_as_class(SocialEventRideRequest)
    print(ride_request.location_ref)
    location = Location.get(ride_request.location_ref)
    event = EventDao().get(ride_request.event_ref)

    # Do Validation Tasks before saving rideRequest
    # 1. Check that rideRequest is not submitted by the same user
    #       for the flight on the same day already
    # TODO: move to transactional logic for better atomicity
    if utils.check_duplicate(ride_request.user_id, ride_request.event_ref):
        raise service_errors.RequestAlreadyExistsError
    # Starts database operations to (save rideRequest and update user's eventSchedule)
    transaction = db.transaction()
    # Transactional business logic for adding rideRequest
    utils.add_ride_request(transaction, ride_request, location, user_id, event)
    # Save write result
    transaction.commit()
    return ride_request
