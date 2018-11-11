"""Author: Zixuan Rao, Andrew Kim
"""

from google.cloud.firestore import DocumentReference

# orbit class

class Orbit:

    firestoreRef: DocumentReference = None

    """ Description	
        This class represents a RideRequest object
    
    """

    @staticmethod
    def from_dict(initial_data):
        return Orbit(initial_data)

    def toDict(self):
        return vars(self)

    def __init__(self, initial_data):
        """ Description
            Initializes a RideRequest Object with python dictionary


        :type self:
        :param self:

        :type dictionary:
        :param dictionary:

        :raises:

        :rtype:
        """

        for key in initial_data:
            setattr(self, key, initial_data[key])
