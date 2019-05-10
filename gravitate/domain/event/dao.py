"""Author: Zixuan Rao, David Nong
"""

from typing import Type

import google
from google.cloud.firestore import Query, Transaction, DocumentReference, DocumentSnapshot
from google.cloud.firestore_v1beta1 import transactional

from gravitate import context
from .models import Event, SocialEvent

CTX = context.Context

db = CTX.db


class EventDao:
    """ Description
        Database access object for events
    """

    def __init__(self):
        self.eventCollectionRef = db.collection('events')

    def get_ref(self, doc_id) -> DocumentReference:
        """ Description
            This method returns EventRef with EventId provided.
            Example: converts "testeventid1" to "/events/testeventid1" of type DocumentReference

        :param doc_id: eventId
        :return:
        """
        eventRef = self.eventCollectionRef.document(doc_id)
        return eventRef

    @staticmethod
    def get_with_transaction(transaction: Transaction, eventRef: DocumentReference) -> Type[Event]:
        """ Description
            Note that this cannot take place if transaction already received write operations.
            "If a transaction is used and it already has write operations added, this method cannot be used
            (i.e. read-after-write is not allowed)."

        :type transaction:Transaction:
        :param transaction:Transaction: firestore transaction
        :type eventRef:DocumentReference:
        :param eventRef:DocumentReference: firestore document reference of the event to get
        :raises:
        :rtype:
        """

        try:
            snapshot: DocumentSnapshot = eventRef.get(
                transaction=transaction)
            snapshotDict: dict = snapshot.to_dict()
            event = Event.from_dict(snapshotDict)
            event.set_firestore_ref(eventRef)
            return event
        except google.cloud.exceptions.NotFound:
            raise Exception('No such document! ' + str(eventRef.id))

    def find_by_timestamp(self, timestamp, category):
        """ Description
            This method finds an airportEvent that "overlaps" with the timestamp provided.

            DEPRECATED

        :param timestamp: the point-in-time that the eventSchedule has to include.
        :return:
        """
        eventId = self._locate_event(timestamp, category)
        eventRef: DocumentReference = self.eventCollectionRef.document(eventId)
        event = Event.from_dict_and_reference(eventRef.get().to_dict(), eventRef)
        return event

    def find_by_date_str(self, date: str, category):
        """
        Find airportEvent that has the matching "localDateString". Note that this finds
            only one event that fits the condition. If there are more in firestore,
            ValueError will be raised

        :param date: local date string eg. "2019-01-01"
        :param category: "airport"
        :raises: ValueError: only exactly 1 event can fit the condition in the database
        :return: one event that fits the condition
        """
        eventDocs = self.eventCollectionRef.where("eventCategory", "==", category)\
            .where("localDateString", "==", date).get()
        events = dict()

        # Loop through each rideRequest
        for doc in eventDocs:

            eventDict = doc.to_dict()
            if eventDict["eventCategory"] != category:
                continue  # Do not consider events of a different category
            eventId = doc.id
            eventRef: DocumentReference = self.eventCollectionRef.document(eventId)
            event = Event.from_dict_and_reference(eventDict, eventRef)

            # Check if the event is in a valid time frame
            events[eventId] = event

        if len(events) == 1:
            return list(events.values())[0]
        elif len(events) > 1:
            raise ValueError("More than 1 event fits the condition. ")
        elif len(events) == 0:
            raise ValueError("No event fits the condition. ")
        else:
            raise ValueError()

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
        _, eventRef = self.eventCollectionRef.add(event.to_dict())
        return eventRef

    def exists_fb_event(self, fb_event_id: str):
        """ Returns doc.id if fb_event_id already exists,
                otherwise return None

        :param fb_event_id:
        :return:
        """
        event_docs = self.eventCollectionRef.where("fbEventId", "==", fb_event_id) \
            .get()
        for doc in event_docs:
            return doc.id
        return None

    def create_fb_event(self, event: SocialEvent) -> DocumentReference:
        """ Creates facebook event in database.

        :param event: event object
        :return: reference to the event just created
        """
        transaction = db.transaction()
        event_ref = self.eventCollectionRef.document(event.fb_event_id)
        self._create_fb_event_transactional(transaction, event, event_ref)
        return event_ref

    @staticmethod
    @transactional
    def _create_fb_event_transactional(transaction, event: SocialEvent, event_ref) -> DocumentReference:
        """ Creates facebook event in database with transaction.

        TODO: remove event_ref from return

        :param transaction: firestore transaction
        :param event: event object
        :param event_ref: document reference for identifying where to save the event to
        :return: reference to the event just created
        """
        snapshot: DocumentSnapshot = event_ref.get(
            transaction=transaction)
        if not snapshot.exists:
            transaction.set(event_ref, event.to_dict())
        return event_ref

    def _locate_event(self, timestamp, category="airport"):
        """ Description
            Uses the timestamp of an event to find the event reference

            Note that no more than event should be found with the timestamp, see preconditions.
            Please check that Firestore has only events of category airport and only one airport event per day.

            TODO: to create composite index: check stack trace and use the link provided

        :param timestamp:
        :param category:

        :raises: google.api_core.exceptions.FailedPrecondition: 400 The query requires an index.

        :return: the first eventId that matches the category and timestamp, or None
        """
        # Grab all of the events in the db
        # Queries for the valid range of events
        # Pre-condition: There is only one airport event, and no social events on the same day
        eventDocs = self.eventCollectionRef.where("eventCategory", "==", category)\
            .where("startTimestamp", "<", timestamp)\
            .order_by("startTimestamp", direction=Query.DESCENDING)\
            .get()

        # Loop through each rideRequest
        for doc in eventDocs:

            eventDict = doc.to_dict()
            if eventDict["eventCategory"] != category:
                continue  # Do not consider events of a different category

            event = Event.from_dict(eventDict)
            eventId = doc.id
            # Check if the event is in a valid time frame
            if event.start_timestamp < timestamp < event.end_timestamp:
                return eventId

        return None

    def get_by_id(self, event_id: str):
        """ Gets an event from database by event id

        :param event_id: id of the event
        :return: event object
        """
        event_ref = self.get_ref(event_id)
        return self.get(event_ref)

    def get(self, eventRef: DocumentReference):
        """ Gets an event from database

        :param eventRef: firestore document reference of the event
        :return: event object
        """
        if isinstance(eventRef, str):
            eventRef = str_to_ref(eventRef)
        snapshot: DocumentSnapshot = eventRef.get()
        snapshotDict: dict = snapshot.to_dict()
        event = Event.from_dict(snapshotDict)
        event.set_firestore_ref(eventRef)
        return event


def str_to_ref(ref_str: str):
    k = ref_str.split("/")
    if k[0] == "":
        k.pop(0)
    return db.document("/".join(k))
