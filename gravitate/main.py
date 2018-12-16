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

from flask import Flask, request
from flask_restful import reqparse, Api, Resource

from google.auth.transport import requests

# Firebase Admin SDK

from firebase_admin import auth
from gravitate.config import Context

# APScheduler for automatic grouping per interval
# Reference: https://stackoverflow.com/questions/21214270/scheduling-a-function-to-run-every-hour-on-flask/38501429
from apscheduler.schedulers.background import BackgroundScheduler

from gravitate.services.grouping_service import OrbitForceMatchService, refreshGroupAll
from gravitate.services.ride_request_service import RideRequestService, DeleteMatchService, DeleteRideRequestService
from gravitate.services.user_service import UserService

sched = BackgroundScheduler(daemon=True)
sched.add_job(refreshGroupAll, 'interval', minutes=1)
sched.start()

# Initialize Flask
firebase_request_adapter = requests.Request()
app = Flask(__name__)
db = Context.db
parser = reqparse.RequestParser()


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
api.add_resource(OrbitForceMatchService, '/devForceMatch')
api.add_resource(EndpointTestService, '/endpointTest')
api.add_resource(DeleteMatchService, '/deleteMatch')
api.add_resource(DeleteRideRequestService, '/deleteRideRequest')


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