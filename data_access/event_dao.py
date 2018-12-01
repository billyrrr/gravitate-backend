"""Author: Zixuan Rao, David Nong
"""

from google.cloud.firestore import Transaction, DocumentReference, DocumentSnapshot, CollectionReference, Client, transactional
from models.ride_request import RideRequest, AirportRideRequest, SocialEventRideRequest
from models.event import Event
import google
from typing import Type
import data_access

CTX = data_access.config.Context

db = CTX.db

class EventDao:
	""" Description	
		Database access object for events

	"""
	def __init__(self):
		self.eventCollectionRef = db.collection('event')

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


	def get(self, eventRef: DocumentReference):
		transaction = db.transaction()
		eventResult = self.getWithTransaction(
			transaction, eventRef)
		transaction.commit()
		return eventResult


	def findByTimestamp(self, timestamp):
		""" Description
			Uses the timestamp of an event to find the event reference
		"""

		# Grab all of the events in the db
		eventDocs = self.eventCollectionRef.get()

		# Loop through each rideRequest
		for doc in eventDocs:
			# Check if the event is in a valid time frame
			if doc.startTimeStamp < timestamp and doc.endTimeStamp > timestamp:
				return doc.eventRef.id

		# If there are no valid events
		return None

	def create(self, event: Type[Event])->DocumentReference:
		""" Description
		:type self:
		:param self:

		:type event:Type[Event]:
		:param event:Type[Event]:

		:raises:

		:rtype:
		"""
		_, eventRef = self.eventCollectionRef.add(event.toDict())
		return eventRef

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

	@transactional
	@staticmethod
	def setWithTransaction(transaction: Transaction, newEvent: Type[Event], eventRef: DocumentReference):
		""" Description
			Note that a read action must have taken place before anything is set with that transaction. 

		:type self:
		:param self:

		:type transaction:Transaction:
		:param transaction:Transaction:

		:type newLocation:Type[Event]:
		:param newLocation:Type[Event]:

		:type eventRef:DocumentReference:
		:param eventRef:DocumentReference:

		:raises:

		:rtype:
		"""
		return transaction.set(eventRef, eventLocation)
	
	
	# The maximum amount of time where a user can request a ride
		# Hard coded to be 1 day in seconds
		# timeDifference = 86400    
		
