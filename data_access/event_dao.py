"""Author: Zixuan Rao, David Nong
"""
from google.cloud.firestore import Transaction, DocumentReference, DocumentSnapshot, CollectionReference, Client, transactional, Query
from models.event import Event
import google
import config
import warnings
from typing import Type

db = config.Context.db


# The maximum amount of time where a user can request a ride
# Hard coded to be 1 day in seconds
timeDifference = 24*60*60

class EventDao:
<<<<<<< HEAD
    """ Description	
        Database access object for events

    """
    def locateAirportEvent(self, timestamp):
        """ Description
            Uses the timestamp of an event to find the event reference
        """

        # Grab all of the events in the db
        eventDocs = self.eventCollectionRef.get()

        # Loop through each rideRequest
        for doc in eventDocs:
            eventDict = doc.to_dict()
            event = Event.fromDict(eventDict)
            eventId = doc.id
            # Check if the event is in a valid time frame
            if event.startTimestamp < timestamp and event.endTimestamp > timestamp:
                return eventId

        return

    def get(self, eventRef: DocumentReference):
        transaction = db.transaction()
        eventResult = self.getWithTransaction(
            transaction, eventRef)
        transaction.commit()
        return eventResult

    
    @transactional
    def getWithTransaction(self, transaction: Transaction, eventRef: DocumentReference) -> Type[Event]:
        """ Description
        	Note that this cannot take place if transaction already received write operations. 
            "If a transaction is used and it already has write operations added, this method cannot be used (i.e. read-after-write is not allowed)."
        :type self:
        :param self:
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
            return event
        except google.cloud.exceptions.NotFound:
            raise Exception('No such document! ' + str(eventRef.id))    

    def findByTimestamp(self, timestamp):
        eventId = self.locateAirportEvent(timestamp)
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

    def __init__(self):
        self.eventCollectionRef = db.collection('events')

    def create(self, event: Event)->DocumentReference:
        _, eventRef = self.eventCollectionRef.add(event.toDict())
        return eventRef
=======
	""" Description	
		Database access object for events

	"""
	def __locateAirportEvent(self, timestamp):
		""" Description
			Uses the timestamp of an event to find the event reference
		"""

		# Grab all of the events in the db
		# Queries for the valid range of events
		# Pre-condition: There is only one airport event, and no social events on the same day
		eventDocs = self.eventCollectionRef.where("startTimestamp", "<", timestamp).order_by("startTimestamp", 
			direction=Query.DESCENDING).limit(1).get()

		# Loop through each rideRequest
		for doc in eventDocs:
			eventDict = doc.to_dict()
			if(eventDict["eventCategory"] == "socialEvent"):
				warnings.warn("The algorithm does not accomodate for social events yet!")

			event = Event.fromDict(eventDict)
			eventId = doc.id
			# Check if the event is in a valid time frame
			if event.startTimestamp < timestamp and event.endTimestamp > timestamp:
				return eventId

		return None

	def get(self, eventRef: DocumentReference):
		transaction = db.transaction()
		eventResult = self.getWithTransaction(
			transaction, eventRef)
		transaction.commit()
		return eventResult

	
	@transactional
	def getWithTransaction(self, transaction: Transaction, eventRef: DocumentReference) -> Type[Event]:
		""" Description
			Note that this cannot take place if transaction already received write operations. 
			"If a transaction is used and it already has write operations added, this method cannot be used (i.e. read-after-write is not allowed)."
		:type self:
		:param self:
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
			return event
		except google.cloud.exceptions.NotFound:
			raise Exception('No such document! ' + str(eventRef.id))    

	def findByTimestamp(self, timestamp):
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

	def __init__(self):
		self.eventCollectionRef = db.collection('events')

	def create(self, event: Event)->DocumentReference:
		_, eventRef = self.eventCollectionRef.add(event.toDict())
		return eventRef
>>>>>>> optimizeTimeStamp
