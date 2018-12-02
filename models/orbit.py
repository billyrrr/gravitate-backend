"""Author: Zixuan Rao, Andrew Kim
"""

from google.cloud.firestore import DocumentReference

# orbit class

class Orbit(object):
    """ Description    
        This class represents a Orbit object
   
    """

    __firestoreRef: DocumentReference = None

    def setFirestoreRef(self, firestoreRef: str):
        self.__firestoreRef = firestoreRef 
    
    def getFirestoreRef(self):
        return self.__firestoreRef
        
    @staticmethod
    def fromDictAndReference(orbitDict, orbitRef):
        orbit = Orbit.fromDict(orbitDict)
        orbit.setFirestoreRef(orbitRef)
        return orbit

    def __init__(self, orbitCategory, eventRef, userTicketPairs, chatroomRef, costEstimate, status):
        """ Description
        This function initializes the Orbit Object
        Note that this function should not be called directly
        
        :param self:
        :param orbitCategory:
        :param eventRef:
        :param userTicketPairs:
        :param chatroomRef:
        :param costEstimate:
        :param status: "1" indicates not ready, "2" indicates ready
        """

        self.orbitCategory = orbitCategory
        self.eventRef = eventRef
        self.userTicketPairs = userTicketPairs
        self.chatroomRef = chatroomRef
        self.costEstimate = costEstimate
        self.status = status

    @staticmethod
    def fromDict(orbitDict):
        """ Description
        This function creates an Orbit
    
        :param orbitDict:
        """
        orbitCategory = orbitDict['orbitCategory']
        eventRef = orbitDict['eventRef']
        userTicketPairs = orbitDict['userTicketPairs']
        chatroomRef = orbitDict['chatroomRef']
        costEstimate = orbitDict['costEstimate']
        status = orbitDict['status']
        return Orbit(orbitCategory, eventRef, userTicketPairs, chatroomRef, costEstimate, status)

    def toDict(self):
        orbitDict = {
            'orbitCategory': self.orbitCategory,
            'eventRef': self.eventRef,
            'userTicketPairs': self.userTicketPairs,
            'chatroomRef': self.chatroomRef,
            'costEstimate': self.costEstimate,
            'status': self.status
        }
        return orbitDict


