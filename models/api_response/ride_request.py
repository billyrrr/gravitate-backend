from models.ride_request import RideRequest
from google.cloud.firestore import DocumentReference
import json

class RideRequestCreationResponse(object):

    def __init__(self, rideRequestRef: DocumentReference):
        self.rideRequestRef = rideRequestRef

    def asJson(self):
        responseDict = {
            'rideRequestRef': self.rideRequestRef.id # TODO change to ref
        }
        return json.dumps(responseDict)
