from flask_restful import Resource

import gravitate.api_server.utils as service_utils
from gravitate.context import Context


db = Context.db


class OrbitCommandService(Resource):
    """
    Handles commands for adding and dropping ride requests from orbit.
    """

    def post(self, orbitId):
        """
        (NOT IMPLEMENTED) Executes a command for adding and dropping ride requests from orbit.

        ---
        tags:
          - orbits
        parameters:
          - name: id
            in: path
            description: ID of the orbit to make changes to
            required: true
            schema:
              type: string
          - name: action
            in: query
            description: one and only one of "drop" and "add"
            required: true
            schema:
              type: string
          - in: body
            name: body
            schema:
              required:
                - rideRequestIds
              properties:
                rideRequestIds:
                  type: array
                  items:
                    descriptions: ride request ids
                    example: "riderequestid1"


        TODO: add gravitate internal server key and admin-authentication
        NOTE: this method is internal; do not call from client
        TODO: implement
        :return:
        """
        raise NotImplementedError


class OrbitService(Resource):

    def get(self, orbitId):
        """
        (NOT IMPLEMENTED) Get the orbit JSON by id

        ---
        tags:
          - orbits
        parameters:
          - name: id
            in: path
            description: ID of the orbit
            required: true
            schema:
              type: string
        responses:
          '200':
            description: orbit response
          default:
            description: unexpected error

        :param rideRequestId:
        :param uid:
        :return:
        TODO: implement
        NOTE: this method should be called/forwarded internally after the authentication
        """
        raise NotImplementedError


class RideRequestOrbitService(Resource):
    """
        /rideRequest/:rideRequestId/orbit/

    """

    @service_utils.authenticate
    def get(self, rideRequestId, uid):
        """
        (NOT IMPLEMENTED) Get the orbit JSON associated with the ride request.

        ---
        tags:
          - rideRequests
        parameters:
          - name: id
            in: path
            description: ID of the ride request associated with the orbit
            required: true
            schema:
              type: string
        responses:
          '200':
            description: orbit response
          default:
            description: unexpected error

        :param rideRequestId:
        :param uid:
        :return:
        TODO: implement

        """

        raise NotImplementedError
