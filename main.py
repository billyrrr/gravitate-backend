# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# TODO adapt with https://flask-restful.readthedocs.io/en/latest/quickstart.html#a-minimal-api

# [START gae_flex_quickstart]
import logging
import json

from flask import Flask, request, jsonify
from flask_restful import reqparse, abort, Api, Resource
from wtforms import Form
import warnings


from models import RideRequest, AirportRideRequest, Target, AirportLocation
from models import User

from forms.ride_request_creation_form import RideRequestCreationForm, RideRequestCreationValidateForm
from forms.user_creation_form import UserCreationForm, UserCreationValidateForm

from controllers import utils, userutils, grouping, eventscheduleutils

from data_access import RideRequestGenericDao, UserDao, EventDao, EventScheduleGenericDao

from google.cloud import firestore
from google.auth.transport import requests
from google.oauth2.id_token import verify_firebase_token


# Firebase Admin SDK

import firebase_admin
from firebase_admin import credentials, auth
from config import Context


# APScheduler for automatic grouping per interval
# Reference: https://stackoverflow.com/questions/21214270/scheduling-a-function-to-run-every-hour-on-flask/38501429
from apscheduler.schedulers.background import BackgroundScheduler

def refreshGroupAll():
    allRideRequestIds = RideRequestGenericDao().getIds(incomplete=True)
    grouping.groupManyRideRequests(allRideRequestIds)

sched = BackgroundScheduler(daemon=True)
sched.add_job(refreshGroupAll, 'interval', minutes=1)
sched.start()


# Initialize Flask
firebase_request_adapter = requests.Request()
app = Flask(__name__)
db = Context.db
parser = reqparse.RequestParser()



class UserService(Resource):
    
    def get(self, uid):
        # Check Firestore to see if UID Already Exists
        if( UserDao().userIdExists(uid)):
            user = UserDao().getUserById(uid)
            userDict = user.toDict()
            return userDict, 200
        else:
            errorResponseDict = {
                "error": "User Does not Exist"
            }
            return errorResponseDict, 400

    def update(self, uid):
        """ Description
            Handles client FCM Token refresh
                https://firebase.google.com/docs/cloud-messaging/android/client#monitor-token-generation
            Note that FCM refresh shall not override the user's settings for enabling notification (if specified in requirement). 

        :type self:
        :param self:

        :type uid:
        :param uid:

        :raises:

        :rtype:
        """
        raise NotImplementedError

    def post(self, uid):
        requestJson = request.get_json()
        requestForm = json.loads(requestJson) if (type(requestJson) != dict) else requestJson

        validateForm = UserCreationValidateForm(data=requestForm)
        
        # POST REQUEST
        if validateForm.validate():

            # Transfer data from validateForm to an internal representation of the form
            form = UserCreationForm()
            validateForm.populate_obj(form)
            userDict = fillUserDictWithForm(form)

            # Create User Object
            newUser: User = User.fromDict(userDict)

            userId = newUser.uid
            userRef = UserDao().userCollectionRef.document(document_id=userId)
            newUser.setFirestoreRef(userRef)
            transaction = db.transaction()

            # Saves User Object to Firestore
            userutils.saveUser(newUser, transaction=transaction)
            userRef = UserDao().userCollectionRef.document(userId)
            transaction.commit()

            responseDict = {"userId": newUser.getFirestoreRef().id}

            return responseDict, 200
        else:
            print(validateForm.errors)
            return validateForm.errors, 400

def fillUserDictWithForm(form: UserCreationForm) -> dict:
    userDict = dict()

    # Move data from the form frontend submitted to userDict
    userDict['uid'] = form.uid
    userDict['membership'] = form.membership
    userDict['display_name'] = form.display_name
    userDict['phone_number'] = form.phone_number
    userDict['photo_url'] = form.photo_url
    userDict['pickupAddress'] = form.pickupAddress

    return userDict

class RideRequestService(Resource):

    def post(self):

        # Verify Firebase auth.

        userId = None # will be filled with auth code
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

            # Starts database operations to save rideRequest and update user's eventSchedule
            # Save rideRequest
            transaction = db.transaction()
            # Saves RideRequest Object to Firestore TODO change to Active Record
            utils.saveRideRequest(transaction, rideRequest)
            userRef = UserDao().userCollectionRef.document(userId)
            transaction.commit()

            # Update the user's eventSchedule
            transaction = db.transaction()
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


class OrbitForceMatchService(Resource):
    def post(self):
        requestJson = request.get_json()
        requestForm = json.loads(requestJson) if (
            type(requestJson) != dict) else requestJson

        operationMode = requestForm.get("operationMode", None)
        rideRequestIds = requestForm.get("rideRequestIds", None) 
        responseDict = None

        if operationMode == "two" and rideRequestIds != None:
            responseDict = grouping.forceMatchTwoRideRequests(rideRequestIds)
        elif operationMode == "many" and rideRequestIds != None:
            grouping.groupManyRideRequests(rideRequestIds)
            responseDict = {"success": True, "operationMode": "many"}
        elif operationMode == "all":
            allRideRequestIds = RideRequestGenericDao().getIds(incomplete=True)
            grouping.groupManyRideRequests(allRideRequestIds)
            responseDict = {"success": True, "opeartionMode": "all"}
        else:
            responseDict = {"error": "Not specified operation mode."}
            return responseDict, 400
        
        # return rideRequest.getFirestoreRef().id, 200
        return responseDict, 200


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
            responseDict = {"success":True}
        except Exception as e:
            responseDict = {"error":dict(e)}
            return responseDict, 500

        # return rideRequest.getFirestoreRef().id, 200
        return responseDict, 200


class DeleteRideRequestService(Resource):
    """ Description	
        Deletes a ride request. 

    """
    def post(self):
        requestJson = request.get_json();
        requestForm = json.loads(requestJson) if (
            type(requestJson) != dict) else requestJson

        userId = requestForm.get("userId", None)
        userRef = UserDao().getRef(userId)
        eventId = requestForm.get("eventId", None)
        eventRef = EventDao().getRef(eventId)
        rideRequestId = requestForm.get("rideRequestId", None)
        rideRequestRef = RideRequestGenericDao().rideRequestCollectionRef.document(rideRequestId)
        
        responseDict = None
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
            EventScheduleGenericDao(userRef=userRef).deleteEvent(eventRef)
            # Delete in RideRequest Collection
            RideRequestGenericDao().delete(rideRequestRef)

        except Exception as e:
            responseDict = {"error":dict(e)}
            return responseDict, 500

        return responseDict, 200
            
    

class EndpointTestService(Resource):
    def post(self):
        """
        * This method handles a POST/PUT call to './authTest' to test that front end Auth
            is set up correctly. 
        If the id_token included in 'Authorization' is verified, the user id (uid)
            corresponding to the id_token will be returned along with other information. 
        Otherwise, an exception is thrown

        """

        # Verify Firebase auth.

        id_token = request.headers['Authorization'].split(' ').pop()

        # Auth code provided by Google
        try:
            # Verify the ID token while checking if the token is revoked by
            # passing check_revoked=True.
            decoded_token = auth.verify_id_token(id_token, check_revoked=True, app=Context.firebaseApp)
            # Token is valid and not revoked.
            uid = decoded_token['uid']
        except auth.AuthError as exc:
            if exc.code == 'ID_TOKEN_REVOKED':
                # Token revoked, inform the user to reauthenticate or signOut().
                return 'Unauthorized. Token revoked, inform the user to reauthenticate or signOut(). ', 401
            else:
                # Token is invalid
                return 'Invalid token', 402

        data = request.get_json()
        responseDict = {'uid': uid, 'request_data': data}
        return responseDict, 200
		

api = Api(app)
api.add_resource(UserService, '/users/<string:uid>')
api.add_resource(RideRequestService, '/rideRequests')
api.add_resource(OrbitForceMatchService, '/devForceMatch' )
api.add_resource(EndpointTestService, '/endpointTest')
api.add_resource(DeleteMatchService, '/deleteMatch')
api.add_resource(DeleteRideRequestService, '/deleteRideRequest')


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
    target = utils.createTargetWithFlightLocalTime(form)
    rideRequestDict['target'] = target.toDict()

    # Set EventRef
    eventRef = utils.findEvent(form)
    rideRequestDict['eventRef'] = eventRef
    location = utils.getAirportLocation(form)
    if not location:
        return rideRequestDict, None
    airportLocationRef = location.getFirestoreRef()
    rideRequestDict['airportLocation'] = airportLocationRef

    return rideRequestDict, location


@app.route('/contextTest', methods=['POST', 'PUT'])
def add_noauth_test_data():
    """ Description
        This endpoint receives a REST API "post_json" call and stores the 
            json in database collection contextText. If set up correctly, 
            the client receives the id of the json inserted. 
        Note that this call does not test Auth token. 

    :raises:

    :rtype:
    """

    current_ride_request_json = request.get_json()
    print(current_ride_request_json)

    ride_requests_ref = db.collection(u'contextText')
    current_ride_request_ref = ride_requests_ref.document()
    current_ride_request_id = current_ride_request_ref.id
    current_ride_request_ref.set(current_ride_request_json)
    return current_ride_request_id, 200



@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_flex_quickstart]
