from gravitate import context
from gravitate.api_server import errors as service_errors
from gravitate.data_access import LocationGenericDao
from gravitate.domain.request_ride import builders as creation_utils, utils
from gravitate.domain.rides import AirportRideRequest, SocialEventRideRequest

db = context.Context.db


def create(args, user_id, ride_category="airport"):
    if ride_category == "airport":
        return _create_airport_ride_request(args, user_id)
    elif ride_category == "event":
        return _create_social_event_ride_request(args, user_id)
    else:
        raise ValueError("ride_category not supported: {}".format(ride_category))


def _create_airport_ride_request(args, user_id):
    builder = creation_utils.AirportRideRequestBuilder()
    ride_request: AirportRideRequest = builder \
        .set_with_form_and_user_id(args, user_id) \
        .build_airport_ride_request() \
        .export_as_class(AirportRideRequest)
    location = LocationGenericDao().get(ride_request.airport_location)
    if ride_request.target.to_event:
        user_location = LocationGenericDao().get(ride_request.origin_ref)
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
    builder = creation_utils.SocialEventRideRequestBuilder()
    ride_request: SocialEventRideRequest = builder \
        .set_with_form_and_user_id(args, user_id) \
        .build_social_event_ride_request() \
        .export_as_class(SocialEventRideRequest)
    print(ride_request.location_ref)
    location = LocationGenericDao().get(ride_request.location_ref)
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
