class RideRequest:
    
    
    """ Description	
        This class represents a RideRequest object
    
    """



    def __init__(self):

        """ Description
            Initializes a RideRequest Object with python dictionary


        :type self:
        :param self:
    
        :type dictionary:
        :param dictionary:
    
        :raises:
    
        :rtype:
        """        
	#instantiate dictionary
	self.dictionary = {"rideCategory":"", "rId":1, "driverStatus":False, "pickupAddress":"", "hasCheckedIn": False, "eventId": 1, "orbitId": 1, "target": "", "pricing": 1, "flightTime": 1, "flightNumber": 1, "airportLocation": 1, "baggages": "", "disabilities": {}, "requestCompletion": False}	
	self.ticket = {"rideRequestId":1, "userWillDrive": False, "hasCheckedIn": False, "inChat": True, "pickupAddress": ""}
