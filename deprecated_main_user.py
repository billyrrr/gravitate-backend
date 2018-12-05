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

from models.user import User

from flask import Flask, request, jsonify
from flask_restful import reqparse, abort, Api, Resource
from wtforms import Form
import warnings

from forms.user_creation_form import UserCreationForm, UserCreationValidateForm
from data_access import UserDao

from controllers import utils
from controllers import userutils

from google.cloud import firestore

from google.auth.transport import requests
from google.oauth2.id_token import verify_firebase_token


# [START] Firebase Admin SDK

import firebase_admin
from firebase_admin import credentials, auth
from config import Context

firebase_request_adapter = requests.Request()
app = Flask(__name__)
db = Context.db
parser = reqparse.RequestParser()

class UserService(Resource):
    
    def get(self, uid):
        # Check Firestore to see if UID Already Exists
        user = UserDao().getUserById(uid)
        if ( user != None ):
            return json.dumps(user.toDict()), 200
            # return user profile
        else:
            return "User Does not Exist", 400


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

            return newUser.getFirestoreRef().id, 200
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

api = Api(app)
api.add_resource(UserService, '/users/<string:uid>')

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
