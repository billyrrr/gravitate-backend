"""Author: David Nong, Zixuan Rao
"""
from abc import ABCMeta, abstractmethod

from gravitate.models.firestore_object import FirestoreObject
from .firestore_object import FirestoreObject


# AirportEventSchedule class

class EventSchedule(FirestoreObject, metaclass=ABCMeta, metaclass=ABCMeta, metaclass=ABCMeta):
    def __init__(self, destName=None, destTime=None, flightTime=None, memberProfilePhotoUrls=None, pickupAddress=None,
                 pending=None, rideRequestRef=None, orbitRef=None, locationRef=None):
        """ Description
        This function initializes the AirportEventSchedule Object
        Note that this function should not be called directly

        :param self:
        :param destName: The destination of the user
        :param destTime: The time when the user will arrive to the airport
        :param flightTime: The time of the flight
        :param memberProfilePhotoUrls: An array of URLs of the other members in the orbit
        :param pickupAddress: The pickup address of the user
        :param pending: "True" not matched into orbit, "False" matched into orbit
        """

        self.destName = destName
        self.destTime = destTime
        self.flightTime = flightTime
        self.memberProfilePhotoUrls = memberProfilePhotoUrls
        self.pickupAddress = pickupAddress
        self.pending = pending
        self.rideRequestRef = rideRequestRef
        self.orbitRef = orbitRef
        self.locationRef = locationRef

    @staticmethod
    @abstractmethod
    def fromDict(eventScheduleDict):
        """ Description
        This function creates an AirportEventSchedule

        :param eventScheduleDict:
        """
        pass

    @staticmethod
    @abstractmethod
    def fromDictAndReference(eventScheduleDict, eventScheduleRef):
        pass

    @abstractmethod
    def toDict(self):
        pass


class AirportEventSchedule(EventSchedule):
    """ Description    
        This class represents the schedule of events for a user.
        Note that the fields are intended to be used only in View layer.
    """

    @staticmethod
    def fromDict(eventScheduleDict):
        """ Description
        This function creates an AirportEventSchedule
    
        :param eventScheduleDict:
        """
        destName = eventScheduleDict['destName']
        destTime = eventScheduleDict['destTime']
        flightTime = eventScheduleDict['flightTime']
        memberProfilePhotoUrls = eventScheduleDict['memberProfilePhotoUrls']
        pickupAddress = eventScheduleDict['pickupAddress']
        pending = eventScheduleDict['pending']
        rideRequestRef = eventScheduleDict['rideRequestRef']
        orbitRef = eventScheduleDict['orbitRef']
        locationRef = eventScheduleDict['locationRef']
        return AirportEventSchedule(destName, destTime, flightTime, memberProfilePhotoUrls, pickupAddress, pending,
                                    rideRequestRef, orbitRef, locationRef)

    @staticmethod
    def fromDictAndReference(eventScheduleDict, eventScheduleRef):
        eventSchedule = AirportEventSchedule.fromDict(eventScheduleDict)
        eventSchedule.setFirestoreRef(eventScheduleRef)
        return eventSchedule

    def toDict(self):
        eventScheduleDict = {
            'destName': self.destName,
            'destTime': self.destTime,
            'flightTime': self.flightTime,
            'memberProfilePhotoUrls': self.memberProfilePhotoUrls,
            'pickupAddress': self.pickupAddress,
            'pending': self.pending,
            'rideRequestRef': self.rideRequestRef,
            'orbitRef': self.orbitRef,
            'locationRef': self.locationRef
        }
        return eventScheduleDict
