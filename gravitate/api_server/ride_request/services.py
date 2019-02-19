"""
Author: Leon Wu, Zixuan Rao

This module implements the service for creating and managing rideRequests.

"""

from flask_restful import Resource

from gravitate.context import Context
from gravitate.domain import request_ride
from gravitate.data_access import RideRequestGenericDao, UserDao, EventScheduleGenericDao
import gravitate.api_server.utils as service_utils
from . import parsers as ride_request_parsers
from gravitate.api_server import errors as service_errors

db = Context.db


class RideRequestCreation(Resource):

    @service_utils.authenticate
    def post(self, rideCategory, uid):
        # Verify Firebase auth.
        user_id = uid

        args = None

        if rideCategory == "airport":
            args = ride_request_parsers.airport_parser.parse_args()

        elif rideCategory == "event":
            args = ride_request_parsers.social_event_ride_parser.parse_args()
        else:
            raise Exception("Unsupported rideType: {}".format(rideCategory))

        print(args)

        # Create RideRequest Object
        ride_request = request_ride.create(args, user_id, ride_category=rideCategory)

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


