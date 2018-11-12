"""Author: Zixuan Rao, Andrew Kim
"""


from google.cloud.firestore import DocumentReference
from models.target import Target, ToEventTarget, FromEventTarget

class RideRequest(object):
    
    __firestoreRef: DocumentReference = None
    
    """ Description	
        This class represents a RideRequest object
    
    """

    def setFirestoreRef(self, firestoreRef: str):
        self.__firestoreRef = firestoreRef 
    
    def getFirestoreRef(self):
        return self.__firestoreRef

    @staticmethod
    def fromDictAndReference(rideRequestDict, rideRequestRef):
        rideRequest = RideRequest.from_dict(rideRequestDict)
        rideRequest.setFirestoreRef(rideRequestRef)
        return rideRequest

    @staticmethod
    def from_dict(rideRequestDict):
        
        rideRequestType = rideRequestDict['rideCategory']

        driverStatus = rideRequestDict['driverStatus']
        pickupAddress = rideRequestDict['pickupAddress']
        hasCheckedIn = rideRequestDict['hasCheckedIn']
        eventRef = rideRequestDict['eventRef']
        orbitRef = rideRequestDict['orbitRef']
        target = Target.createTarget(rideRequestDict['target'])

        if rideRequestType == 'airportRide':
            return AirportRideRequest(driverStatus, pickupAddress, hasCheckedIn, eventRef, orbitRef, target)
        elif rideRequestType == 'eventRide':
            return SocialEventRideRequest(driverStatus, pickupAddress, hasCheckedIn, eventRef, orbitRef, target)
        else:
            raise Exception('Not supported rideRequestType: {}'.format(rideRequestType))

    def to_dict(self):
        # TODO implement
        return vars(self)

    def __init__(self, driverStatus, pickupAddress, hasCheckedIn, eventRef, orbitRef, target):

        """ Description
            Initializes a RideRequest Object with python dictionary


        :type self:
        :param self:
    
        :type dictionary:
        :param dictionary:
    
        :raises:
    
        :rtype:
        """

        self.driverStatus = driverStatus
        self.pickupAddress = pickupAddress
        self.hasCheckedIn = hasCheckedIn
        self.eventRef = eventRef
        self.orbitRef = orbitRef
        self.target = target

class AirportRideRequest(RideRequest):

    # TODO more arguments
    def __init__(self, driverStatus, pickupAddress, hasCheckedIn, eventRef, orbitRef, target):

        """ Description
            Initializes an AirportRideRequest Object with python dictionary


        :type self:
        :param self:
    
        :type dictionary:
        :param dictionary:
    
        :raises:
    
        :rtype:
        """        

        super().__init__(driverStatus, pickupAddress, hasCheckedIn, eventRef, orbitRef, target)

class SocialEventRideRequest(RideRequest):

    # TODO more arguments
    def __init__(self, driverStatus, pickupAddress, hasCheckedIn, eventRef, orbitRef, target):

        """ Description
            Initializes a SocialEventRideRequest Object with python dictionary


        :type self:
        :param self:
    
        :type dictionary:
        :param dictionary:
    
        :raises:
    
        :rtype:
        """        

        super().__init__(driverStatus, pickupAddress, hasCheckedIn, eventRef, orbitRef, target)