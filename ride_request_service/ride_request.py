from ride_request_service.process_ride_request import buildAirportRideRequestWithForm
from forms.ride_request_creation_form import RideRequestCreationForm
from data_access.ride_request_dao import RideRequestGenericDao
from models.api_response.ride_request import RideRequestCreationResponse


def create(rideRequestCreationForm: RideRequestCreationForm):
    """ Description
        This function is to be called by REST API endpoint layer

        :type rideRequestCreationForm:RideRequestCreationForm:
        :param rideRequestCreationForm:RideRequestCreationForm:
    
        :raises:
    
        :rtype:
    """
    
    rideRequest = buildAirportRideRequestWithForm(rideRequestCreationForm)
    
    rideRequestRef = RideRequestGenericDao().createRideRequest(rideRequest)
    response = RideRequestCreationResponse(rideRequestRef)
    return response.asJson()