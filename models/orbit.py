"""Author: Zixuan Rao, Andrew Kim
"""

from google.cloud.firestore import DocumentReference

# orbit class

class Orbit(object):
    """ Description	
        This class represents a RideRequest object
    
    """

    __firestoreRef: DocumentReference = None

    def setFirestoreRef(self, firestoreRef: str):
        self.__firestoreRef = firestoreRef 
    
    def getFirestoreRef(self):
        return self.__firestoreRef

    @staticmethod
    def fromDict(orbitDict):
        # TODO implement
        return Orbit()

    def toDict(self):
        # TODO implment
        pass

    def __init__(self):
        # TODO implement
        pass
