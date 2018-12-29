"""
Author: Leon Wu, Zixuan Rao

This module implements the service for creating and managing rideRequests.

"""

import json

from flask import request
from flask_restful import Resource

from gravitate.context import Context
from gravitate.controllers import utils, grouping
from gravitate.data_access import RideRequestGenericDao, UserDao, EventScheduleGenericDao, LocationGenericDao
from gravitate.forms.ride_request_creation_form import AirportRideRequestCreationForm
from gravitate.models import AirportRideRequest, RideRequest
import gravitate.services.utils as service_utils
import gravitate.services.ride_request.utils as creation_utils
from . import parsers as ride_request_parsers

db = Context.db


class AirportRideRequestCreationService(Resource):

    """
    This class replaces web-form with reqparse for form validation.
    """
    @service_utils.authenticate
    def post(self, uid):

        # Verify Firebase auth.
        user_id = uid

        args = ride_request_parsers.airport_parser.parse_args()

        # Retrieve JSON
        # form = AirportRideRequestCreationForm.from_dict(args)

        # # Create WTForm for validating the fields
        # validateForm = RideRequestCreationValidateForm(
        #     data=requestForm)

        # # Mock userId and eventId. Delete before release
        # userId = 'SQytDq13q00e0N3H4agR'
        # warnings.warn("using test user ids, delete before release")

        # if not validateForm.validate():
        #     print(validateForm.errors)
        #     return validateForm.errors, 400
        #
        # # Transfer data from validateForm to an internal representation of the form
        # form = AirportRideRequestCreationForm()
        # validateForm.populate_obj(form)
        #
        # rideRequestDict, location = fill_ride_request_dict_with_form(
        #     form, userId)
        # if not location:
        #     errorResponseDict = {
        #         "error": "invalid airport code and datetime combination or error finding airport location in backend",
        #         "originalArgs": args
        #     }
        #     return errorResponseDict, 400

        # Create RideRequest Object
        builder = creation_utils.AirportRideRequestBuilder()
        ride_request: AirportRideRequest = builder\
            .set_with_form_and_user_id(args, user_id)\
            .build_airport_ride_request()\
            .export_as_class(AirportRideRequest)
        location = LocationGenericDao().get(ride_request.airportLocation)

        # Do Validation Tasks before saving rideRequest
        # 1. Check that rideRequest is not submitted by the same user
        #       for the flight on the same day already
        # TODO: move to transactional logic for better atomicity
        if utils.check_duplicate(ride_request.user_id, ride_request.event_ref):
            error_response_dict = {
                "error": "Ride request on the same day (for the same event) already exists",
                "originalArgs": args
            }
            return error_response_dict, 400
        # Ends validation tasks

        # Starts database operations to (save rideRequest and update user's eventSchedule)
        transaction = db.transaction()

        # Transactional business logic for adding rideRequest
        utils.add_ride_request(transaction, ride_request, location, user_id)

        # Save write result
        transaction.commit()

        # rideRequest Response
        response_dict = {
        "id": ride_request.get_firestore_ref().id
        ,"firestoreRef": ride_request.get_firestore_ref().id}

        return response_dict, 200


    @service_utils.authenticate
    def patch(self, uid):
        """
        TODO implement

        This method modifies fields in an airportRideRequest.
            Allow user to patch these fields at any time:
                * disabilities
                * pickupAddress
                * "baggages"
            If the rideRequest is not matched into an orbit, allow user to patch these fields:
                * driverStatus
                furthermore, if flightLocalTime still in the same event and eventLocation is "LAX",
                    * flightLocalTime
                    * earliest
                    * latest
                    * flightNumber


        Note that this operation should be done in a transaction to ensure atomicity of the operation.

        :param uid:
        :return:
        """
        raise NotImplementedError


class CityRideRequestService(Resource):

    def get(self):
        """
        This method reads arguments from url string and creates a cityRideRequest.
            For reference, see GET in airportRideRequest.

        TODO implement
        :return:
        """

        raise NotImplementedError


class DeleteMatchService(Resource):
    def post(self):
        request_json = request.get_json()
        request_form = json.loads(request_json) if (
                type(request_json) != dict) else request_json

        ride_request_id = request_form.get("rideRequestId", None)
        response_dict = None

        try:
            ride_request_ref = RideRequestGenericDao().rideRequestCollectionRef.document(ride_request_id)
            grouping.remove(ride_request_ref)
            response_dict = {"success": True}
        except Exception as e:
            print(e)
            response_dict = {"error": str(e)}
            return response_dict, 500

        # return rideRequest.get_firestore_ref().id, 200
        return response_dict, 200


class AirportRideRequestService(Resource):
    """ Description
        Deletes a ride request.

    """

    @service_utils.authenticate
    def delete(self, rideRequestId, uid):
        """
        Replaces POST "/deleteRideRequest"
        :param rideRequestId:
        :param uid:
        :return:
        """
        # requestJson = request.get_json()
        # requestForm = json.loads(requestJson) if (
        #         type(requestJson) != dict) else requestJson

        user_id = uid
        user_ref = UserDao().get_ref(user_id)
        ride_request_ref = RideRequestGenericDao().rideRequestCollectionRef.document(rideRequestId)

        response_dict = {}
        ride_request = RideRequestGenericDao().get(ride_request_ref)
        event_id = ride_request.event_ref.id

        print("userId: {}, rideRequestId: {}, eventId: {}".format(user_id, rideRequestId, event_id))

        # Validate that the ride request is not matched to an orbit
        request_completion = ride_request.request_completion
        if request_completion:
            response_dict = {
                "error": "Ride request has requestCompletion as True. Unmatch from an orbit first. "
            }
            return response_dict, 500

        try:
            # Delete in User's Event Schedule
            EventScheduleGenericDao(userRef=user_ref).delete_event_by_id(event_id)
            # Delete in RideRequest Collection
            RideRequestGenericDao().delete(ride_request_ref)
            response_dict = {"success": True}

        except Exception as e:
            err_str = str(e)
            response_dict = {"error": "Error occurred deleting rideRequest and eventSchedule: " + err_str}
            return response_dict, 500

        return response_dict, 200


class DeleteRideRequestService(Resource):
    """ Description
        DEPRECATED: moved to DELETE '/rideRequests/$rideRequestId'
        Deletes a ride request.
    """

    def post(self):
        request_json = request.get_json()
        request_form = json.loads(request_json) if (
                type(request_json) != dict) else request_json

        user_id = request_form.get("userId", None)
        user_ref = UserDao().get_ref(user_id)
        event_id = request_form.get("eventId", None)
        ride_request_id = request_form.get("rideRequestId", None)
        ride_request_ref = RideRequestGenericDao().rideRequestCollectionRef.document(ride_request_id)

        response_dict = {}
        ride_request = RideRequestGenericDao().get(ride_request_ref)

        # Validate that the ride request is not matched to an orbit
        request_completion = ride_request.requestCompletion
        if request_completion:
            response_dict = {
                "error": "Ride request has requestCompletion as True. Unmatch from an orbit first. "
            }
            return response_dict, 500

        try:
            # Delete in User's Event Schedule
            EventScheduleGenericDao(userRef=user_ref).delete_event_by_id(event_id)
            # Delete in RideRequest Collection
            RideRequestGenericDao().delete(ride_request_ref)
            response_dict = {"success": True}

        except Exception as e:
            err_str = str(e)
            response_dict = {"error": "Error occurred deleting rideRequest and eventSchedule: " + err_str}
            return response_dict, 500

        return response_dict, 200
