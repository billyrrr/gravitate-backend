"""
Author: Leon Wu, Zixuan Rao

This module implements the service for creating and managing rideRequests.

"""

import json

from flask import request
from flask_restful import Resource

from gravitate.context import Context
from gravitate.domain.grouping import grouping
from gravitate.domain import request_ride
from gravitate.data_access import RideRequestGenericDao, UserDao, EventScheduleGenericDao
import gravitate.services.utils as service_utils
from . import parsers as ride_request_parsers
from gravitate.services import errors as service_errors

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

        # if not location:
        #     errorResponseDict = {
        #         "error": "invalid airport code and datetime combination or error finding airport location in backend",
        #         "originalArgs": args
        #     }
        #     return errorResponseDict, 400

        # Create RideRequest Object
        ride_request = request_ride.create(args, user_id)

        # rideRequest Response
        response_dict = {
            "id": ride_request.get_firestore_ref().id,
            "firestoreRef": ride_request.get_firestore_ref().id}

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

        ride_request_ref = RideRequestGenericDao().rideRequestCollectionRef.document(ride_request_id)
        r = RideRequestGenericDao().get(ride_request_ref)
        location_ref = r.airport_location
        grouping.drop_group({ride_request_id},
                            orbit_id=r.orbit_ref.id,
                            event_id=r.event_ref.id,
                            location_id=location_ref.id)
        response_dict = {"success": True}

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
            raise service_errors.RequestAlreadyMatchedError
            # response_dict = {
            #     "error": "Ride request has requestCompletion as True. Un-match from an orbit first. "
            # }
            # return response_dict, 500

        try:
            # Delete in User's Event Schedule
            EventScheduleGenericDao(userRef=user_ref).delete_event_by_id(event_id)
            # Delete in RideRequest Collection
            RideRequestGenericDao().delete(ride_request_ref)
            response_dict = {"success": True}

        except Exception as e:
            err_str = str(e)
            response_dict = {"error": "Error occurred deleting rideRequest and eventSchedule: " + err_str}
            print(response_dict)
            return response_dict, 500

        return response_dict, 200
