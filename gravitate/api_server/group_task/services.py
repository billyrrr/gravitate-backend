import json
from functools import wraps

from flask import request
from flask_restful import Resource, abort
from werkzeug.exceptions import Unauthorized

from gravitate.domain.rides import RideRequestGenericDao
from gravitate.domain.group import actions


def validate_cron(func):
    """
        Wraps a resource to assert that the method is called by Appengine-Cron.
        https://cloud.google.com/appengine/docs/standard/python3/scheduling-jobs-with-cron-yaml
        TODO: Note that this method does not validate IP address
    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        is_cron = request.headers.get('X-Appengine-Cron')

        if is_cron is None or not is_cron:
            raise Unauthorized(description='Unauthorized. This resource must be run with Appengine-Cron. ')

        return func(*args, **kwargs)

    return wrapper


class GroupCronTasksService(Resource):
    """

    This service further decouples cron task from instance, and allow tasks to be queued for better
        performance during peak.
    """

    @validate_cron
    def get(self):
        """
        Triggers an automatic grouping for all incomplete requests. \
            (temporary: will migrate to other ways to trigger grouping) \
            Can only be called by google cloud cron tasks.

        ---
        tags:
          - groupAll
          # operationId: find ride request by id

        responses:
            '200':
              description: successful operation
              properties:
                success:
                  type: boolean
                  example: true
                operationMode:
                  type: string
                  example: all
            '403':
              description: Unauthorized. This resource must be run with Appengine-Cron.
            default:
              description: unexpected error
        """
        all_ride_request_ids = RideRequestGenericDao().get_ids(incomplete=True)
        actions.group_many(all_ride_request_ids)
        response_dict = {"success": True, "operationMode": "all"}
        return response_dict, 200


class GroupTasksService(Resource):
    """
    This class provides RESTful Resource for matching rideRequests.
    The service will match rideRequests in ways specified in the json that is posted to /groupTasks endpoint.
    """

    def post(self):
        """
        Matches rideRequests in ways specified in the given json

        ---
        tags:
          - groupTasks

        parameters:
          - in: body
            name: body
            schema:
              id: GroupTask
              required:
                - operationMode
              properties:
                operationMode:
                  type: string
                  enum:
                    - two
                    - many
                    - all
                rideRequestIds:
                  type: array
                  items:
                    name: rideRequestId
                    type: string
                    example: "riderequestid1"

        responses:
          '200':
            description: successful operation
            properties:
              success:
                type: boolean
                example: true
              operationMode:
                type: string
                example: all

          '400':
            description: unexpected error
            properties:
              error:
                description: error message
                example: "Not specified operation mode."
        """
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
