import json

from flask import request
from flask_restful import Resource

from gravitate.controllers import grouping
from gravitate.data_access import RideRequestGenericDao


class OrbitForceMatchService(Resource):
    """
    This class provides service layer functionality for force matching rideRequests.
        This service should be used in development environment to force a match for testing purposes.
    """
    def post(self):
        requestJson = request.get_json()
        requestForm = json.loads(requestJson) if (
                type(requestJson) != dict) else requestJson

        operationMode = requestForm.get("operationMode", None)
        rideRequestIds = requestForm.get("rideRequestIds", None)
        responseDict = None

        if operationMode == "two" and rideRequestIds != None:
            responseDict = grouping.forceMatchTwo(rideRequestIds)
        elif operationMode == "many" and rideRequestIds != None:
            grouping.groupMany(rideRequestIds)
            responseDict = {"success": True, "operationMode": "many"}
        elif operationMode == "all":
            allRideRequestIds = RideRequestGenericDao().getIds(incomplete=True)
            grouping.groupMany(allRideRequestIds)
            responseDict = {"success": True, "operationMode": "all"}
        else:
            responseDict = {"error": "Not specified operation mode."}
            return responseDict, 400

        # return rideRequest.getFirestoreRef().id, 200
        return responseDict, 200


def refreshGroupAll():
    """ Description
    This function corresponds to use case "group ride requests".

    :return:
    """
    allRideRequestIds = RideRequestGenericDao().getIds(incomplete=True)
    grouping.groupMany(allRideRequestIds)
