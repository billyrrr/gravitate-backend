"""
Author: Andrew Kim
Reviewer: Zixuan Rao
"""

from google.cloud.firestore import DocumentReference
from .firestore_object import FirestoreObject


# event class
class Event(FirestoreObject):
    """ Description
    this class represents the event object
        Note that reference to the object eventRef is deprecated.
        Get and set firestoreRef instead.

    """

    @staticmethod
    def from_dict_and_reference(eventDict, eventRef):
        event = Event.from_dict(eventDict)
        event.set_firestore_ref(eventRef)
        return event

    @staticmethod
    def from_dict(eventDict):
        """ Description
            This function creates an event

            :param eventDict:
        """
        eventCategory = eventDict['eventCategory']
        participants = eventDict['participants']
        eventLocation = eventDict['eventLocation']
        startTimestamp = eventDict['startTimestamp']
        endTimestamp = eventDict['endTimestamp']
        pricing = eventDict['pricing']
        locationRef = eventDict['locationRef']
        isClosed = eventDict['isClosed']

        return Event(eventCategory, participants, eventLocation, startTimestamp, endTimestamp, pricing, locationRef,
                     isClosed)

    def to_dict(self):
        eventDict = {
            'eventCategory': self.eventCategory,
            'participants': self.participants,
            'eventLocation': self.eventLocation,
            'startTimestamp': self.startTimestamp,
            'endTimestamp': self.endTimestamp,
            'pricing': self.pricing,
            'locationRef': self.locationRef,
            'isClosed': self.isClosed
        }
        return eventDict

    def set_as_active(self):
        """ Definition
            Sets the boolean isClosed to False

            :param self:
        """
        self.isClosed = False

    def set_as_passed(self):
        """ Definition
            Sets the boolean isClosed to True

            :param self:
        """
        self.isClosed = True

    def __init__(self, eventCategory, participants, eventLocation, startTimestamp, endTimestamp, pricing, locationRef,
                 isClosed):
        """Description
           This function initializes an Event object

           :param self:
           :param eventCategory:
           :param participants:
           :param eventLocation:
           :param startTimestamp:
           :param endTimestamp:
           :param pricing:
           :param locationRef: a list of locationRef that corresponds to this event
           :param isClosed:
        """
        self.eventCategory = eventCategory
        self.participants = participants
        self.eventLocation = eventLocation
        self.startTimestamp = startTimestamp
        self.endTimestamp = endTimestamp
        self.pricing = pricing
        self.locationRef = locationRef
        self.isClosed = isClosed
