"""
Author: Leon Wu, Zixuan Rao

This module implements the service for creating and managing rideRequests.

"""

import json

from flask import request
from flask_restful import Resource

from gravitate.context import Context
from gravitate.controllers import utils
from gravitate.controllers.grouping import grouping
from gravitate.data_access import RideRequestGenericDao, UserDao, EventScheduleGenericDao, LocationGenericDao
from gravitate.models import AirportRideRequest, SocialEventRideRequest
import gravitate.services.utils as service_utils
import gravitate.services.ride_request.utils as creation_utils
from . import parsers as ride_request_parsers
from gravitate.services import errors as service_errors

db = Context.db


class SocialEventRideRequestCreationService(Resource):
    """
    This class replaces web-form with reqparse for form validation.
    """

    @service_utils.authenticate
    def post(self, uid):
        raise NotImplementedError # TODO: implement
        # Verify Firebase auth.
        user_id = uid

        args = ride_request_parsers.social_event_ride_parser.parse_args()

        # if not location:
        #     errorResponseDict = {
        #         "error": "invalid airport code and datetime combination or error finding airport location in backend",
        #         "originalArgs": args
        #     }
        #     return errorResponseDict, 400

        # Create RideRequest Object
        builder = creation_utils.SocialEventRideRequestBuilder()
        ride_request: SocialEventRideRequest = builder \
            .set_with_form_and_user_id(args, user_id) \
            .build_social_event_ride_request() \
            .export_as_class(SocialEventRideRequest)
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

        # rideRequest Response
        response_dict = {
            "id": ride_request.get_firestore_ref().id,
            "firestoreRef": ride_request.get_firestore_ref().id}

        return response_dict, 200

