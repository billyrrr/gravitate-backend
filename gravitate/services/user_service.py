"""
Author: Leon Wu
Reviewer: Zixuan Rao
"""

import json

from flask import request
from flask_restful import Resource

from gravitate.controllers import userutils
from gravitate.data_access import UserDao
from gravitate.forms.user_creation_form import UserCreationValidateForm, UserCreationForm
from gravitate.models import User
from gravitate.config import Context

db = Context.db


class UserService(Resource):

    def get(self, uid):
        # Check Firestore to see if UID Already Exists
        if (UserDao().userIdExists(uid)):
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
            Note that FCM refresh shall not override the user's settings for enabling notification
                (if specified in requirement).

        :type self:
        :param self:

        :type uid:
        :param uid:

        :raises:

        :rtype:
        """
        raise NotImplementedError

    def post(self, uid):
        """ Description:
            This method handles POST request to handle use case "create ride request"

        :param uid:
        :return:
        """
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
