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


class LocationService(Resource):
    """
    This class allows user to create an event.
    """

    @service_utils.authenticate
    def post(self, uid):
        """
        TODO: implement

        This method allows the user to post a location.
            Expect a JSON form in request.json

        Form fields required (Note that field names are different from location model):
            "category": "campus",
            "coordinates": {
                "latitude": 34.414132,
                "longitude": -119.848868
            },
            "address": "C572+HC Isla Vista, California",
            "name": "University of California, Santa Barbara"

        Validation:
            Reject if:
                eventCategory is "airport", or is not one of "campus", "social"
                locationRef is the same as any airport locationRef
                ...
            Allow pricing to be empty, and fill in default value

        Workflow:
            ...
            Generate campusCode from name

        Note that this method is only for generating location of an event. User-specific pick up and drop off
            are represented with address string, so there is no need to call this endpoint.

        :param uid:
        :return:
        """
        raise NotImplementedError
