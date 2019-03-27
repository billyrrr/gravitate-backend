"""Author: Zixuan Rao, Andrew Kim
"""

# orbit class
from gravitate.models.firestore_object import FirestoreObject


class Orbit(FirestoreObject):
    """ Description    
        This class represents a Orbit object
   
    """

    @staticmethod
    def from_dict_and_reference(orbit_dict, orbit_ref):
        orbit = Orbit.from_dict(orbit_dict)
        orbit.set_firestore_ref(orbit_ref)
        return orbit

    def __init__(self, orbit_category, event_ref, user_ticket_pairs, chatroom_ref, cost_estimate, status):
        """ Description
        This function initializes the Orbit Object
        Note that this function should not be called directly
        
        :param self:
        :param orbit_category:
        :param event_ref:
        :param user_ticket_pairs:
        :param chatroom_ref:
        :param cost_estimate:
        :param status: "1" indicates not ready, "2" indicates ready
        """

        super().__init__()
        self.orbit_category = orbit_category
        self.event_ref = event_ref
        self.user_ticket_pairs = user_ticket_pairs
        self.chatroom_ref = chatroom_ref
        self.cost_estimate = cost_estimate
        self.status = status

    @staticmethod
    def from_dict(orbitDict):
        """ Description
        This function creates an Orbit
    
        :param orbitDict:
        """
        orbit_category = orbitDict['orbitCategory']
        event_ref = orbitDict['eventRef']
        user_ticket_pairs = orbitDict['userTicketPairs']
        chatroom_ref = orbitDict['chatroomRef']
        cost_estimate = orbitDict['costEstimate']
        status = orbitDict['status']
        return Orbit(orbit_category, event_ref, user_ticket_pairs, chatroom_ref, cost_estimate, status)

    def to_dict(self):
        orbit_dict = {
            'orbitCategory': self.orbit_category,
            'eventRef': self.event_ref,
            'userTicketPairs': self.user_ticket_pairs,
            'chatroomRef': self.chatroom_ref,
            'costEstimate': self.cost_estimate,
            'status': self.status
        }
        return orbit_dict


