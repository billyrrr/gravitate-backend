import json

from flask import request
from flask_restful import Resource

from gravitate.domain.group import actions
from gravitate.domain.rides import RideRequestGenericDao


class OrbitForceMatchService(Resource):
    """
    This class provides service layer functionality for force matching rideRequests.
        This service should be used in development environment to force a match for testing purposes.
    """
    def post(self):
        request_json = request.get_json()
        request_form = json.loads(request_json) if (
                type(request_json) != dict) else request_json

        operation_mode = request_form.get("operationMode", None)
        ride_request_ids = request_form.get("rideRequestIds", None)
        response_dict = None

        if operation_mode == "two" and ride_request_ids is not None:
            response_dict = actions.group_two(ride_request_ids)
        elif operation_mode == "many" and ride_request_ids is not None:
            actions.group_many(ride_request_ids)
            response_dict = {"success": True, "operationMode": "many"}
        elif operation_mode == "all":
            all_ride_request_ids = RideRequestGenericDao().get_ids(incomplete=True)
            actions.group_many(all_ride_request_ids)
            response_dict = {"success": True, "operationMode": "all"}
        else:
            response_dict = {"error": "Not specified operation mode."}
            return response_dict, 400

        # return rideRequest.get_firestore_ref().id, 200
        return response_dict, 200


def refreshGroupAll():
    """ Description
    This function corresponds to use case "grouping ride requests".

    :return:
    """
    allRideRequestIds = RideRequestGenericDao().get_ids(incomplete=True)
    actions.group_many(allRideRequestIds)


class DeleteMatchService(Resource):
    def post(self):
        request_json = request.get_json()
        request_form = json.loads(request_json) if (
                type(request_json) != dict) else request_json

        ride_request_id = request_form.get("rideRequestId", None)

        ride_request_ref = RideRequestGenericDao().rideRequestCollectionRef.document(ride_request_id)
        r = RideRequestGenericDao().get(ride_request_ref)
        location_ref = r.airport_location
        actions.drop_group({ride_request_id},
                           orbit_id=r.orbit_ref.id,
                           event_id=r.event_ref.id,
                           location_id=location_ref.id)
        response_dict = {"success": True}

        return response_dict, 200


class DeleteMatchServiceNew(Resource):

    def post(self, rideRequestId):

        ride_request_id = rideRequestId

        ride_request_ref = RideRequestGenericDao().rideRequestCollectionRef.document(ride_request_id)
        r = RideRequestGenericDao().get(ride_request_ref)
        location_ref = r.airport_location
        actions.drop_group({ride_request_id},
                           orbit_id=r.orbit_ref.id,
                           event_id=r.event_ref.id,
                           location_id=location_ref.id)
        response_dict = {"success": True}

        return response_dict, 200
