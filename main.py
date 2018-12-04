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

from models import RideRequest, AirportRideRequest, Target, AirportLocation

from flask import Flask, request, jsonify
from flask_restful import reqparse, abort, Api, Resource
from wtforms import Form
import warnings

from forms.ride_request_creation_form import RideRequestCreationForm, RideRequestCreationValidateForm
from controllers import utils
from controllers import group_user
from controllers import grouping

from google.cloud import firestore
from google.auth.transport import requests
from google.oauth2.id_token import verify_firebase_token
from controllers import eventscheduleutils
from data_access.ride_request_dao import RideRequestGenericDao
from data_access.user_dao import UserDao
from data_access.event_dao import EventDao

# [START] Firebase Admin SDK

import firebase_admin
from firebase_admin import credentials, auth
from config import Context

firebase_request_adapter = requests.Request()
app = Flask(__name__)
db = Context.db
parser = reqparse.RequestParser()


@app.route('/hello')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello World!'


class RideRequestService(Resource):

    def post(self):
        requestJson = request.get_json()
        requestForm = json.loads(requestJson) if (
            type(requestJson) != dict) else requestJson

        validateForm = RideRequestCreationValidateForm(
            data=requestForm)

        # Mock userId and eventId. Delete before release
        userId = 'SQytDq13q00e0N3H4agR'
        warnings.warn("using test user ids, delete before release")

        # POST REQUEST
        if validateForm.validate():

            # Transfer data from validateForm to an internal representation of the form
            form = RideRequestCreationForm()
            validateForm.populate_obj(form)

            rideRequestDict, location = fillRideRequestDictWithForm(
                form, userId)

            # Create RideRequest Object
            rideRequest: AirportRideRequest = RideRequest.fromDict(
                rideRequestDict)
            # print(rideRequest.toDict())

            rideRequestId = utils.randomId()
            rideRequestRef = RideRequestGenericDao(
            ).rideRequestCollectionRef.document(document_id=rideRequestId)
            rideRequest.setFirestoreRef(rideRequestRef)
            transaction = db.transaction()

            # Saves RideRequest Object to Firestore TODO change to Active Record
            utils.saveRideRequest(rideRequest, transaction=transaction)
            userRef = UserDao().userCollectionRef.document(userId)
            eventSchedule = eventscheduleutils.buildEventSchedule(
                rideRequest, location)
            UserDao.addToEventScheduleWithTransaction(
                transaction, userRef=userRef, eventRef=rideRequest.eventRef, eventSchedule=eventSchedule)
            transaction.commit()

            # rideRequest Response
            responseDict = {"FirestoreRef": rideRequest.getFirestoreRef().id}
            # return rideRequest.getFirestoreRef().id, 200
            return json.dumps(responseDict), 200
        else:
            print(validateForm.errors)
            return validateForm.errors, 400


class OrbitForceMatchService(Resource):
    def post(self):
        requestJson = request.get_json()
        requestForm = json.loads(requestJson) if (
            type(requestJson) != dict) else requestJson

        # requestForm = {
        #     "rideRequestRefs": []
        # }

        rideRequestIds = requestForm["rideRequestIds"]
        rideRequests = list()
        for rideRequestId in rideRequestIds:
            rideRequestRef = db.collection("rideRequests").document(rideRequestId)
            rideRequest = RideRequestGenericDao().getRideRequest(rideRequestRef)
            rideRequest.setFirestoreRef(rideRequestRef)
            rideRequests.append(rideRequest)

        numRideRequests = len(rideRequests)
        assert numRideRequests >= 2
        if numRideRequests >= 3:
            warnings.warn(
                "Orbit is only tested for matching 2 rideRequests. " +
                "You are forcing to match {} users in one orbit. ".format(numRideRequests) +
                "Only rideRequests {} and {} are expected be matched. "
                    .format(rideRequests[0].toDict(), rideRequests[1].toDict()))

        pairedTuples = [(rideRequests[0], rideRequests[1])]

        groups = list()
        grouping.constructGroups(groups, pairedTuples)
        
        group = groups[0]
        notJoined = group.doWork()

        # rideRequest Response
        responseDict = {"notJoined": notJoined}
        # return rideRequest.getFirestoreRef().id, 200
        return json.dumps(responseDict), 200


api = Api(app)
api.add_resource(RideRequestService, '/rideRequests')
api.add_resource(OrbitForceMatchService, '/devForceMatch' )


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


@app.route('/authTest', methods=['POST', 'PUT'])
def add_auth_test_data():
    """
    * This method handles a POST/PUT call to './authTest' to test that front end Auth
        is set up correctly. 
    If the id_token included in 'Authorization' is verified, the user id (uid)
        corresponding to the id_token will be returned along with other information. 
    Otherwise, an exception is thrown

    """

    # Verify Firebase auth.

    id_token = request.headers['Authorization'].split(' ').pop()

    # [Start] provided by Google
    try:
        # Verify the ID token while checking if the token is revoked by
        # passing check_revoked=True.
        decoded_token = auth.verify_id_token(id_token, check_revoked=True)
        # Token is valid and not revoked.
        uid = decoded_token['uid']
    except auth.AuthError as exc:
        if exc.code == 'ID_TOKEN_REVOKED':
            # Token revoked, inform the user to reauthenticate or signOut().
            return 'Unauthorized. Token revoked, inform the user to reauthenticate or signOut(). ', 401
        else:
            # Token is invalid
            return 'Invalid token', 402
    # [End] provided by google

    # uid = decoded_token['uid']

    data = request.get_json()

    return json.dumps({'uid': uid, 'request_data': data}), 200


@app.route('/notes', methods=['POST', 'PUT'])
def add_note():
    """
    * Example Method provided by Google
    Adds a note to the user's notebook. The request should be in this format:

        {
            "message": "note message."
        }
    """

    # Verify Firebase auth.
    id_token = request.headers['Authorization'].split(' ').pop()
    claims = verify_firebase_token(
        id_token, firebase_request_adapter)
    if not claims:
        return 'Unauthorized', 401

    # [START gae_python_create_entity]
    data = request.get_json()

    # # Populates note properties according to the model,
    # # with the user ID as the key name.
    # note = Note(
    #     parent=ndb.Key(Note, claims['sub']),
    #     message=data['message'])

    # # Some providers do not provide one of these so either can be used.
    # note.friendly_id = claims.get('name', claims.get('email', 'Unknown'))
    # # [END gae_python_create_entity]

    # # Stores note in database.
    # note.put()

    return json.dumps(data), 200


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
