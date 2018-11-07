from google.cloud import firestore
from models.ride_request import RideRequest

def createRideRequest(rr: dict, collectionRef: firestore.CollectionReference):
    rideRequest = RideRequest(rr, "For demo. Delete before development. ")
    rideRequestDict = rideRequest.todict()
    collectionRef.add(rideRequestDict)