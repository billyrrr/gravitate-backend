"""Author: David Nong
"""

from google.cloud.firestore import DocumentReference

# EventSchedule class

class EventSchedule(object):
    """ Description    
        This class represents the schedule of events for a user
    """

    __firestoreRef: DocumentReference = None

    def setFirestoreRef(self, firestoreRef: str):
        self.__firestoreRef = firestoreRef 
    
    def getFirestoreRef(self):
        return self.__firestoreRef
        
    @staticmethod
    def fromDictAndReference(EventScheduleDict, EventScheduleRef):
        EventSchedule = EventSchedule.fromDict(EventScheduleDict)
        EventSchedule.setFirestoreRef(EventScheduleRef)
        return EventSchedule

    def __init__(self, destName, destTime, flightName, memberProfilePhoto, pickupAddress, status):
        """ Description
        This function initializes the EventSchedule Object
        Note that this function should not be called directly
        
        :param self:
        :param destName: The destination of the user
        :param destTime: The time when the user will arrive to the airport
        :param flightName: The time of the flight
        :param memberProfilePhoto: An array of URLs of the other members in the orbit 
        :param pickupAddress: The pickup address of the user
        :param status: "1" indicates not ready, "2" indicates ready
        """

        self.destName = destName
        self.destTime = destTime
        self.flightName = flightName
        self.memberProfilePhoto = memberProfilePhoto
        self.pickupAddress = pickupAddress
        self.status = status

    @staticmethod
    def fromDict(EventScheduleDict):
        """ Description
        This function creates an EventSchedule
    
        :param EventScheduleDict:
        """
        destName = EventScheduleDict['destName']
        destTime = EventScheduleDict['destTime']
        flightName = EventScheduleDict['flightName']
        memberProfilePhoto = EventScheduleDict['memberProfilePhoto']
        pickupAddress = EventScheduleDict['pickupAddress']
        status = EventScheduleDict['status']
        return EventSchedule(destName, destTime, flightName, memberProfilePhoto, pickupAddress, status)

    def toDict(self):
        EventScheduleDict = {
            'destName': self.destName,
            'destTime': self.destTime,
            'flightName': self.flightName,
            'memberProfilePhoto': self.memberProfilePhoto
            'pickupAddress': self.pickupAddress,
            'status': self.status
        }
        return EventScheduleDict


