"""Author: Zixuan Rao, Andrew Kim
"""

# orbit class
from gravitate.models.firestore_object import FirestoreObject


class Orbit(FirestoreObject):
    """ Description    
        This class represents a Orbit object
   
    """

    @staticmethod
    def from_dict_and_reference(orbitDict, orbitRef):
        orbit = Orbit.from_dict(orbitDict)
        orbit.set_firestore_ref(orbitRef)
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
    def from_dict(orbitDict):
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

    def to_dict(self):
        orbitDict = {
            'orbitCategory': self.orbitCategory,
            'eventRef': self.eventRef,
            'userTicketPairs': self.userTicketPairs,
            'chatroomRef': self.chatroomRef,
            'costEstimate': self.costEstimate,
            'status': self.status
        }
        return orbitDict


