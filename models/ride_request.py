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
        rideRequest = RideRequest.fromDict(rideRequestDict)
        rideRequest.setFirestoreRef(rideRequestRef)
        return rideRequest

    @staticmethod
    def fromDict(rideRequestDict):
        
        rideRequestType = rideRequestDict['rideCategory']

        driverStatus = rideRequestDict['driverStatus']
        pickupAddress = rideRequestDict['pickupAddress']
        hasCheckedIn = rideRequestDict['hasCheckedIn']
        eventRef = rideRequestDict['eventRef']
        orbitRef = rideRequestDict['orbitRef']
        target = Target.createTarget(rideRequestDict['target'])

        if rideRequestType == 'airportRide':
            flightLocalTime = rideRequestDict['flightLocalTime']
            flightNumber = rideRequestDict['flightNumber']
            airportLocation = rideRequestDict['airportLocation']
            baggages = rideRequestDict['baggages']
            disabilities = rideRequestDict['disabilities']

            # TODO change function calls
            return AirportRideRequest(driverStatus, pickupAddress, hasCheckedIn, eventRef, orbitRef, target)
        elif rideRequestType == 'eventRide':
            return SocialEventRideRequest(driverStatus, pickupAddress, hasCheckedIn, eventRef, orbitRef, target)
        else:
            raise Exception('Not supported rideRequestType: {}'.format(rideRequestType))

    def toDict(self):
        rideRequestDict = {
            'driverStatus': self.driverStatus,
            'pickupAddress': self.pickupAddress,
            'hasCheckedIn': self.hasCheckedIn,
            'eventRef': self.eventRef,
            'orbitRef': self.orbitRef,
            'target': self.target.toDict()
        }
        return rideRequestDict

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
        self.rideCategory = 'airportRide'

    def toDict(self):
        rideRequestDict = super().toDict()
        rideRequestDict['rideCategory'] = 'airportRide'
        return rideRequestDict

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
        self.rideCategory = 'eventRide'

    def toDict(self):
        rideRequestDict = super().toDict()
        rideRequestDict['rideCategory'] = 'eventRide'
        return rideRequestDict
