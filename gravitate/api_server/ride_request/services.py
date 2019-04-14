"""
Author: Leon Wu, Zixuan Rao

This module implements the service for creating and managing rideRequests.

"""
from flask import request
from flask_restful import Resource, HTTPException

import gravitate.api_server.utils as service_utils
from gravitate.api_server import errors as service_errors
from gravitate.context import Context
from gravitate.data_access import UserDao, EventScheduleGenericDao
from gravitate.domain.rides import RideRequestGenericDao
from gravitate.domain import rides
from gravitate.domain.luggage import actions as luggage_actions
from gravitate.domain.luggage.models import Luggages
from . import parsers as ride_request_parsers

db = Context.db


class MovedPermanently(HTTPException):
    code = 301
    description = "Resource moved permanently. "


class RideRequestCreation(Resource):

    @service_utils.authenticate
    def post(self, rideCategory, uid):

        raise MovedPermanently("Resource moved permanently. POST to /rideRequests instead. ")


class RideRequestPost(Resource):

    @service_utils.authenticate
    def post(self, uid):
        # Verify Firebase auth.
        user_id = uid

        # Get ride category
        json_object = request.get_json()
        ride_category = json_object.get("rideCategory")
        if ride_category is None:
            raise Exception("rideCategory not specified. ")

        args = None

        if ride_category == "airport":
            args = ride_request_parsers.airport_parser.parse_args()

        elif ride_category == "event":
            args = ride_request_parsers.social_event_ride_parser.parse_args()
        else:
            raise Exception("Unsupported rideType: {}".format(ride_category))

        print(args)

        # Create RideRequest Object
        ride_request = rides.create(args, user_id, ride_category=ride_category)

        # rideRequest Response
        response_dict = {
            "id": ride_request.get_firestore_ref().id,
            "firestoreRef": ride_request.get_firestore_ref().id  # Legacy support
        }

        return response_dict, 200


class RideRequestService(Resource):
    """ Description
        Deletes a ride request.

    """

    @service_utils.authenticate
    def get(self, rideRequestId, uid):
        """
        Get the JSON for ride request
        :param rideRequestId:
        :param uid:
        :return:
        """
        user_id = uid

        # TODO: validate that the user has permission to view the ride request

        ride_request_ref = RideRequestGenericDao().rideRequestCollectionRef.document(rideRequestId)

        ride_request = RideRequestGenericDao().get(ride_request_ref)

        print("userId: {}, rideRequestId: {}".format(user_id, rideRequestId))

        response_dict = ride_request.to_dict_view()
        response_dict["pickupAddress"] = ride_request.pickup_address

        return response_dict, 200

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


class LuggageService(Resource):

    """
        /rideRequest/:rideRequestId/luggage/

    """

    @service_utils.authenticate
    def get(self, rideRequestId, uid):
        """
        Get the JSON for the luggage associatedd with ride request
        :param rideRequestId:
        :param uid:
        :return:
        """
        user_id = uid

        # TODO: validate that the user has permission to view the ride request

        ride_request_ref = RideRequestGenericDao().rideRequestCollectionRef.document(rideRequestId)

        ride_request = RideRequestGenericDao().get(ride_request_ref)

        print("userId: {}, rideRequestId: {}".format(user_id, rideRequestId))

        response_dict = ride_request.to_dict_view()["baggages"]

        return response_dict, 200

    @service_utils.authenticate
    def put(self, rideRequestId, uid):
        """

        :param rideRequestId:
        :param uid:
        :return:
        """
        args = ride_request_parsers.luggage_parser.parse_args()

        luggage_list = args["luggages"]
        luggages = Luggages()
        luggages.add_from_list(luggage_list)

        # add_luggage_nontransactional(rideRequestId, luggages)
        luggage_actions.put_luggages(ride_request_id=rideRequestId, luggages=luggages)

        response_dict = {"newLuggageValues": luggages.to_dict()}

        return response_dict, 200


def add_luggage_nontransactional(rideRequestId, luggages):
    """
    Add luggage to a rideRequest without a transaction (non-atomic). Using this method may result in modifications
        done to rideRequest to be overridden.
    :param rideRequestId:
    :return:
    """
    rideRequest = RideRequestGenericDao().get_by_id(rideRequestId)
    rideRequest.baggages = luggages.to_dict()
    RideRequestGenericDao().set(rideRequest)
