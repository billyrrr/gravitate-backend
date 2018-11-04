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

# [START gae_flex_quickstart]
import logging

import json

from flask import Flask, request

from google.cloud import firestore
from google.auth.transport import requests
from google.oauth2.id_token import verify_firebase_token

# [START] Firebase Admin SDK

import firebase_admin
from firebase_admin import credentials, auth

cred = credentials.Certificate("./cse110-vibe-firebase-adminsdk-ib702-3d408a5927.json")
firebase_admin.initialize_app(cred)

# [END] Firebase Admin SDK

firebase_request_adapter = requests.Request()

app = Flask(__name__)
db = firestore.Client()

@app.route('/hello')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello World!'

@app.route('/createRideRequest', methods=['POST', 'PUT'])
def createRideRequest():
    # TODO implement
    return 

@app.route('/')

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

    ride_requests_ref = db.collection(u'contextText')
    current_ride_request_ref = ride_requests_ref.document()
    current_ride_request_id = current_ride_request_ref.id
    current_ride_request_ref.set(current_ride_request_json)
    return current_ride_request_id, 200

@app.route('/authTest', methods=['POST', 'PUT'])
def add_auth_test_data():
    """
    * Example Method provided by Google
    Adds a note to the user's notebook. The request should be in this format:

        {
            "message": "note message."
        }
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
            pass
        else:
            # Token is invalid
            pass
    # [End]

    # if not claims:
    #     return 'Unauthorized', 401
    
    uid = decoded_token['uid']
    

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

    return json.dumps({'uid':uid, 'request_data':data}), 200

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
