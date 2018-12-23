import json

from firebase_admin import auth
from flask import request
from flask_restful import Resource

from gravitate.config import Context
from gravitate.controllers import utils, eventscheduleutils, grouping
from gravitate.data_access import RideRequestGenericDao, UserDao, EventScheduleGenericDao
from gravitate.forms.ride_request_creation_form import RideRequestCreationValidateForm, AirportRideRequestCreationForm
from gravitate.models import AirportRideRequest, RideRequest, AirportLocation
import gravitate.services.utils as service_utils

import warnings
from flask_restful import reqparse

db = Context.db


class AirportRideRequestService(Resource):

    @service_utils.authenticate
    def post(self, uid):

        # Verify Firebase auth.
        userId = uid

        # Retrieve JSON
        requestJson = request.get_json()
        requestForm = json.loads(requestJson) if (
                type(requestJson) != dict) else requestJson

        # Create WTForm for validating the fields
        validateForm = RideRequestCreationValidateForm(
            data=requestForm)

        # # Mock userId and eventId. Delete before release
        # userId = 'SQytDq13q00e0N3H4agR'
        # warnings.warn("using test user ids, delete before release")

        if not validateForm.validate():
            print(validateForm.errors)
            return validateForm.errors, 400

        # Transfer data from validateForm to an internal representation of the form
        form = AirportRideRequestCreationForm()
        validateForm.populate_obj(form)

        rideRequestDict, location = fillRideRequestDictWithForm(
            form, userId)
        if not location:
            errorResponseDict = {
                "error": "invalid airport code and datetime combination or error finding airport location in backend",
                "originalForm": requestForm
            }
            return errorResponseDict, 400

        # Create RideRequest Object
        rideRequest: AirportRideRequest = RideRequest.fromDict(
            rideRequestDict)

        # Do Validation Tasks before saving rideRequest
        # 1. Check that rideRequest is not submitted by the same user
        #       for the flight on the same day already
        if utils.hasDuplicateEvent(rideRequest.userId, rideRequest.eventRef):
            errorResponseDict = {
                "error": "Ride request on the same day (for the same event) already exists",
                "originalForm": requestForm
            }
            return errorResponseDict, 400
        # Ends validation tasks

        # Starts database operations to (save rideRequest and update user's eventSchedule)
        transaction = db.transaction()

        # Transactional business logic for adding rideRequest
        utils.addRideRequest(transaction, rideRequest, location, userId)

        # Save write result
        transaction.commit()

        # rideRequest Response
        responseDict = {"firestoreRef": rideRequest.getFirestoreRef().id}

        return responseDict, 200

class AirportRideRequestServiceReqParse(Resource):
    """
    This class replaces web-form with reqparse for form validation.
    """

    @service_utils.authenticate
    def post(self, uid):

        userId = uid

        # Parse field values from url path
        parser = reqparse.RequestParser()
        parser.add_argument('flightNumber', type=str, help='Flight Number')
        parser.add_argument('airportCode', type=str, help='Airport Code')
        parser.add_argument('flightLocalTime', type=str, help='Flight Local Time ISO8601')
        parser.add_argument('pickupAddress', type=str, help='Pickup Address')
        parser.add_argument('toEvent', type=bool, help='whether the ride is heading to the event')
        parser.add_argument('driverStatus', type=bool,
                            help="whether the user want to be considered as a driver for the event")
        args = parser.parse_args()
        form = AirportRideRequestCreationForm.from_dict(args)

        rideRequestDict, location = fillRideRequestDictWithForm(
            form, userId)
        if not location:
            errorResponseDict = {
                "error": "invalid airport code and datetime combination or error finding airport location in backend",
                "originalReq": request.args.to_dict()
            }
            return errorResponseDict, 400

        # Create RideRequest Object
        rideRequest: AirportRideRequest = RideRequest.fromDict(
            rideRequestDict)

        # Do Validation Tasks before saving rideRequest
        # 1. Check that rideRequest is not submitted by the same user
        #       for the flight on the same day already
        if utils.hasDuplicateEvent(rideRequest.userId, rideRequest.eventRef):
            errorResponseDict = {
                "error": "Ride request on the same day (for the same event) already exists",
                "originalForm": request.args.to_dict()
            }
            return errorResponseDict, 400
        # Ends validation tasks

        # Starts database operations to (save rideRequest and update user's eventSchedule)
        transaction = db.transaction()

        # Transactional business logic for adding rideRequest
        utils.addRideRequest(transaction, rideRequest, location, userId)

        # Save write result
        transaction.commit()

        # rideRequest Response
        responseDict = {"firestoreRef": rideRequest.getFirestoreRef().id}

        return responseDict, 200


def fillRideRequestDictWithForm(form: AirportRideRequestCreationForm, userId) -> (dict, AirportLocation):
    """ Description
        This method fills a rideRequest dict that can later be used to call RideRequest().fromDict method.

    :param form:
    :param userId:
    :return: a tuple of rideRequest dict and AirportLocation
    """
    rideRequestDict = dict()

    rideRequestDict['rideCategory'] = 'airportRide'

    # Move data from the form frontend submitted to rideRequestDict
    rideRequestDict['pickupAddress'] = form.pickupAddress
    rideRequestDict['driverStatus'] = form.driverStatus
    rideRequestDict['flightLocalTime'] = form.flightLocalTime
    rideRequestDict['flightNumber'] = form.flightNumber

    # Fields to be filled "immediately"

    # TODO fill unspecified options with default values
    rideRequestDict['pricing'] = 987654321  # TODO change

    # Populate rideRequestDict with default service data
    rideRequestDict['disabilities'] = dict()
    rideRequestDict['baggages'] = dict()
    rideRequestDict['hasCheckedIn'] = False
    rideRequestDict['orbitRef'] = None
    rideRequestDict['userId'] = userId
    rideRequestDict['requestCompletion'] = False

    # Fields to be filled "after some thinking"

    # Set Target
    target = utils.createTargetWithFlightLocalTime(form.flightLocalTime, form.toEvent)
    rideRequestDict['target'] = target.toDict()

    # Set EventRef
    eventRef = utils.findEvent(form.flightLocalTime)
    rideRequestDict['eventRef'] = eventRef
    location = utils.getAirportLocation(form.airportCode)
    if not location:
        return rideRequestDict, None
    airportLocationRef = location.getFirestoreRef()
    rideRequestDict['airportLocation'] = airportLocationRef

    return rideRequestDict, location


class DeleteMatchService(Resource):
    def post(self):
        requestJson = request.get_json()
        requestForm = json.loads(requestJson) if (
                type(requestJson) != dict) else requestJson

        rideRequestId = requestForm.get("rideRequestId", None)
        responseDict = None

        try:
            rideRequestRef = RideRequestGenericDao().rideRequestCollectionRef.document(rideRequestId)
            grouping.remove(rideRequestRef)
            responseDict = {"success": True}
        except Exception as e:
            print(e)
            responseDict = {"error": str(e)}
            return responseDict, 500

        # return rideRequest.getFirestoreRef().id, 200
        return responseDict, 200


class DeleteRideRequestService(Resource):
    """ Description
        Deletes a ride request.

    """

    def post(self):
        requestJson = request.get_json()
        requestForm = json.loads(requestJson) if (
                type(requestJson) != dict) else requestJson

        userId = requestForm.get("userId", None)
        userRef = UserDao().getRef(userId)
        eventId = requestForm.get("eventId", None)
        rideRequestId = requestForm.get("rideRequestId", None)
        rideRequestRef = RideRequestGenericDao().rideRequestCollectionRef.document(rideRequestId)

        responseDict = {}
        rideRequest = RideRequestGenericDao().get(rideRequestRef)

        # Validate that the ride request is not matched to an orbit
        requestCompletion = rideRequest.requestCompletion
        if requestCompletion:
            responseDict = {
                "error": "Ride request has requestCompletion as True. Unmatch from an orbit first. "
            }
            return responseDict, 500

        try:
            # Delete in User's Event Schedule
            EventScheduleGenericDao(userRef=userRef).deleteEventById(eventId)
            # Delete in RideRequest Collection
            RideRequestGenericDao().delete(rideRequestRef)
            responseDict = {"success": True}

        except Exception as e:
            errStr = str(e)
            responseDict = {"error": "Error occurred deleting rideRequest and eventSchedule: " + errStr}
            return responseDict, 500

        return responseDict, 200
