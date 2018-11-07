from models.ride_request import RideRequest

def createRideRequest(rr: dict):
    rideRequest = RideRequest(rr, "For demo. Delete before development. ")
    rideRequestDict = rideRequest.todict()
    return rideRequestDict