import json

from firebase_admin import auth
from flask import request
from flask_restful import Resource

from gravitate.context import Context
from gravitate.controllers import utils, eventscheduleutils, grouping
from gravitate.data_access import RideRequestGenericDao, UserDao, EventScheduleGenericDao
from gravitate.forms.ride_request_creation_form import RideRequestCreationValidateForm, AirportRideRequestCreationForm
from gravitate.models import AirportRideRequest, RideRequest, AirportLocation
import gravitate.services.utils as service_utils

import warnings
from flask_restful import reqparse

db = Context.db


class EventService(Resource):
    """
    This class allows user to create an event.
    """

    @service_utils.authenticate
    def post(self, uid):
        """
        TODO: implement

        This method allows the user to post an event.
            Expect a JSON form in request.json
        For now, handle only local time in "America/Los_Angeles"

        Form fields required:
            "eventCategory": "campus" | "social"
            "eventLocation" (A user-defined text description such as "LAX")
            "locationRef" (Should have been generated by earlier steps in workflow)
            "startLocalTime"
            "endLocalTime"
            "pricing": 100

        Validation:
            Reject if:
                eventCategory is "airport", or is not one of "campus", "social"
                locationRef is the same as any airport locationRef
                ...
            Allow pricing to be empty, and fill in default value



        :param uid:
        :return:
        """
        raise NotImplementedError
