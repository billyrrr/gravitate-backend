import json

from flask import request
from flask_restful import Resource

from gravitate.domain.rides import RideRequestGenericDao
from gravitate.domain.group import actions


class GroupTasksService(Resource):
    """
    This class provides RESTful Resource for matching rideRequests. The service will match rideRequests
        in ways specified in the json that is posted to /groupTasks endpoint.
    This service further decouples cron task from instance, and allow tasks to be queued for better
        performance during peak.
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
