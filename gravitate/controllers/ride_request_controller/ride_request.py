from gravitate.controllers import utils
from gravitate.controllers.ride_request_controller import utils as creation_utils
from gravitate.data_access import LocationGenericDao
from gravitate.models import AirportRideRequest
from gravitate.services import errors as service_errors
from gravitate.services.ride_request.services import db


def create(args, user_id):
    builder = creation_utils.AirportRideRequestBuilder()
    ride_request: AirportRideRequest = builder \
        .set_with_form_and_user_id(args, user_id) \
        .build_airport_ride_request() \
        .export_as_class(AirportRideRequest)
    location = LocationGenericDao().get(ride_request.airport_location)
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
