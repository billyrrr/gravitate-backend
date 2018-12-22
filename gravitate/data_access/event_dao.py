"""Author: Zixuan Rao, David Nong
"""

from google.cloud.firestore import Query, Transaction, DocumentReference, DocumentSnapshot, CollectionReference, Client, \
    transactional
from gravitate.models import RideRequest, AirportRideRequest, Event
import google
from typing import Type
import warnings
from gravitate import config

CTX = config.Context

db = CTX.db


class EventDao:
    """ Description
        Database access object for events
    """

    def __init__(self):
        self.eventCollectionRef = db.collection('events')

    def getRef(self, id) -> DocumentReference:
        """ Description
            This method returns EventRef with EventId provided.
            Example: converts "testeventid1" to "/events/testeventid1" of type DocumentReference

        :param id: eventId
        :return:
        """
        eventRef = self.eventCollectionRef.document(id)
        return eventRef

    @staticmethod
    # @transactional
    def getWithTransaction(transaction: Transaction, eventRef: DocumentReference) -> Type[Event]:
        """ Description
            Note that this cannot take place if transaction already received write operations.
            "If a transaction is used and it already has write operations added, this method cannot be used
            (i.e. read-after-write is not allowed)."

        :type transaction:Transaction:
        :param transaction:Transaction:
        :type eventRef:DocumentReference:
        :param eventRef:DocumentReference:
        :raises:
        :rtype:
        """

        try:
            snapshot: DocumentSnapshot = eventRef.get(
                transaction=transaction)
            snapshotDict: dict = snapshot.to_dict()
            event = Event.fromDict(snapshotDict)
            event.setFirestoreRef(eventRef)
            return event
        except google.cloud.exceptions.NotFound:
            raise Exception('No such document! ' + str(eventRef.id))

    def findByTimestamp(self, timestamp):
        """ Description
            This method finds an airportEvent that "overlaps" with the timestamp provided.

        :param timestamp: the point-in-time that the eventSchedule has to include.
        :return:
        """
        eventId = self.__locateAirportEvent(timestamp)
        eventRef: DocumentReference = self.eventCollectionRef.document(eventId)
        event = Event.fromDictAndReference(eventRef.get().to_dict(), eventRef)
        return event

    def delete(self, eventRef: DocumentReference):
        """ Description
            This function deletes a ride request from the database
        :type self:
        :param self:
        :type eventRef:DocumentReference:
        :param eventRef:DocumentReference:
        :raises:
        :rtype:
        """
        return eventRef.delete()

    def create(self, event: Event) -> DocumentReference:
        _, eventRef = self.eventCollectionRef.add(event.toDict())
        return eventRef

    def __locateAirportEvent(self, timestamp):
        """ Description
            Uses the timestamp of an event to find the event reference

            Note that no more than event should be found with the timestamp, see preconditions.
            Please check that Firestore has only events of category airport and only one airport event per day.
        """

        # Grab all of the events in the db
        # Queries for the valid range of events
        # Pre-condition: There is only one airport event, and no social events on the same day
        eventDocs = self.eventCollectionRef.where("startTimestamp", "<", timestamp)\
            .order_by("startTimestamp", direction=Query.DESCENDING)\
            .get()

        count = 0

        # Loop through each rideRequest
        for doc in eventDocs:

            count += 1
            if count == 2:
                warnings.warn()

            eventDict = doc.to_dict()
            if (eventDict["eventCategory"] == "socialEvent"):
                warnings.warn("The algorithm does not accomodate for social events yet!")

            event = Event.fromDict(eventDict)
            eventId = doc.id
            # Check if the event is in a valid time frame
            if event.startTimestamp < timestamp and event.endTimestamp > timestamp:
                return eventId

        return None




    def get(self, eventRef: DocumentReference):
        snapshot: DocumentSnapshot = eventRef.get()
        snapshotDict: dict = snapshot.to_dict()
        event = Event.fromDict(snapshotDict)
        event.setFirestoreRef(eventRef)
        return event
        return eventResult
