from models.ride_request import RideRequest

def createRideRequestFromForm(form: dict):
    rideRequestDict = dict()

    # TODO move data from the form frontend submitted to rideRequestDict
    rideRequestDict['pickupAddress'] = form['pickupAddress']

    # TODO fill unspecified options with default values
    if ('disabilities' in form):
        # If 'disabilities' is defined in the form submitted
        rideRequestDict['disabilities'] = form['disabilities']
    else:
        # If 'disabilities' not defined, set an empty dict as value
        rideRequestDict['disabilities'] = dict()

    # TODO populate rideRequestDict with default service data
    rideRequestDict['hasCheckedIn'] = False

    rideRequest = RideRequest.fromDict(rideRequestDict)
    return rideRequest