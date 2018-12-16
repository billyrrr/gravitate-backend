import json

from firebase_admin import auth
from flask import request
from flask_restful import Resource

from gravitate.config import Context
from gravitate.controllers import utils, eventscheduleutils, grouping
from gravitate.data_access import RideRequestGenericDao, UserDao, EventScheduleGenericDao
from gravitate.forms.ride_request_creation_form import RideRequestCreationValidateForm, RideRequestCreationForm
from gravitate.models import AirportRideRequest, RideRequest, AirportLocation

import warnings

db = Context.db

class RideRequestServiceTempTesting(Resource):

    def post(self):

        warnings.warn("Running temp testing service. Change back before release. ")

        # Retrieve JSON
        requestJson = request.get_json()
        requestForm = json.loads(requestJson) if (
                type(requestJson) != dict) else requestJson

        userId = requestForm['testUserId']  # will be filled with auth code

        # Create WTForm for validating the fields
        validateForm = RideRequestCreationValidateForm(
            data=requestForm)

        # # Mock userId and eventId. Delete before release
        # userId = 'SQytDq13q00e0N3H4agR'
        # warnings.warn("using test user ids, delete before release")

        if validateForm.validate():

            # Transfer data from validateForm to an internal representation of the form
            form = RideRequestCreationForm()
            validateForm.populate_obj(form)

            rideRequestDict, location = fillRideRequestDictWithForm(
                form, userId)
            if not location:
                errorResponseDict = {
                    "error": "invalid airport code or error finding airport location in backend",
                    "originalForm": requestForm
                }
                return errorResponseDict, 400

            # Create RideRequest Object
            rideRequest: AirportRideRequest = RideRequest.fromDict(
                rideRequestDict)
            # print(rideRequest.toDict())

            rideRequestId = utils.randomId()
            rideRequestRef = RideRequestGenericDao(
            ).rideRequestCollectionRef.document(document_id=rideRequestId)
            rideRequest.setFirestoreRef(rideRequestRef)

            # Do Validation Tasks before saving rideRequest
            # 1. Check that rideRequest is not submitted by the same user
            #       for the flight on the same day alreaddy
            duplicateEvent = utils.hasDuplicateEvent(rideRequest.userId, rideRequest.eventRef)
            if duplicateEvent:
                errorResponseDict = {
                    "error": "Ride request on the same day (for the same event) already exists",
                    "originalForm": requestForm
                }
                return errorResponseDict, 400
            # Ends validation tasks

            # Starts database operations to save rideRequest and update user's eventSchedule
            # Save rideRequest
            transaction = db.transaction()
            # Saves RideRequest Object to Firestore TODO change to Active Record
            utils.saveRideRequest(transaction, rideRequest)
            userRef = UserDao().userCollectionRef.document(userId)





            # transaction.commit()
            #
            # # Update the user's eventSchedule
            # transaction = db.transaction()





            eventSchedule = eventscheduleutils.buildEventSchedule(
                rideRequest, location)
            UserDao.addToEventScheduleWithTransaction(
                transaction, userRef=userRef, eventRef=rideRequest.eventRef, eventSchedule=eventSchedule)
            transaction.commit()

            # rideRequest Response
            responseDict = {"firestoreRef": rideRequest.getFirestoreRef().id}
            # return rideRequest.getFirestoreRef().id, 200
            return responseDict, 200
        else:
            print(validateForm.errors)
            return validateForm.errors, 400



class RideRequestService(Resource):

    def post(self):

        # Verify Firebase auth.

        userId = None  # will be filled with auth code
        id_token = request.headers['Authorization'].split(' ').pop()

        # Auth code provided by Google
        try:
            # Verify the ID token while checking if the token is revoked by
            # passing check_revoked=True.
            decoded_token = auth.verify_id_token(id_token, check_revoked=True, app=Context.firebaseApp)
            # Token is valid and not revoked.
            uid = decoded_token['uid']
            # Set userId to firebaseUid
            userId = uid
        except auth.AuthError as exc:
            if exc.code == 'ID_TOKEN_REVOKED':
                # Token revoked, inform the user to reauthenticate or signOut().
                errorResponseDict = {
                    'error': 'Unauthorized. Token revoked, inform the user to reauthenticate or signOut(). '
                }
                return errorResponseDict, 401
            else:
                # Token is invalid
                errorResponseDict = {
                    'error': "Invalid token"
                }
                return errorResponseDict, 402

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

        if validateForm.validate():

            # Transfer data from validateForm to an internal representation of the form
            form = RideRequestCreationForm()
            validateForm.populate_obj(form)

            rideRequestDict, location = fillRideRequestDictWithForm(
                form, userId)
            if not location:
                errorResponseDict = {
                    "error": "invalid airport code or error finding airport location in backend",
                    "originalForm": requestForm
                }
                return errorResponseDict, 400

            # Create RideRequest Object
            rideRequest: AirportRideRequest = RideRequest.fromDict(
                rideRequestDict)
            # print(rideRequest.toDict())

            rideRequestId = utils.randomId()
            rideRequestRef = RideRequestGenericDao(
            ).rideRequestCollectionRef.document(document_id=rideRequestId)
            rideRequest.setFirestoreRef(rideRequestRef)

            # Do Validation Tasks before saving rideRequest
            # 1. Check that rideRequest is not submitted by the same user
            #       for the flight on the same day alreaddy
            duplicateEvent = utils.hasDuplicateEvent(rideRequest.userId, rideRequest.eventRef)
            if duplicateEvent:
                errorResponseDict = {
                    "error": "Ride request on the same day (for the same event) already exists",
                    "originalForm": requestForm
                }
                return errorResponseDict, 400
            # Ends validation tasks

            # Starts database operations to (save rideRequest and update user's eventSchedule)
            transaction = db.transaction()


            # Saves RideRequest Object to Firestore TODO change to Active Record
            utils.saveRideRequest(transaction, rideRequest)
            userRef = UserDao().userCollectionRef.document(userId)

            # Update the user's eventSchedule
            eventSchedule = eventscheduleutils.buildEventSchedule(
                rideRequest, location)
            UserDao.addToEventScheduleWithTransaction(
                transaction, userRef=userRef, eventRef=rideRequest.eventRef, eventSchedule=eventSchedule)


            transaction.commit()

            # rideRequest Response
            responseDict = {"firestoreRef": rideRequest.getFirestoreRef().id}
            # return rideRequest.getFirestoreRef().id, 200
            return responseDict, 200
        else:
            print(validateForm.errors)
            return validateForm.errors, 400


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
            responseDict = {"error": "Error occured deleting rideRequest and eventSchedule: " + errStr}
            return responseDict, 500

        return responseDict, 200


def fillRideRequestDictWithForm(form: RideRequestCreationForm, userId) -> (dict, AirportLocation):
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
