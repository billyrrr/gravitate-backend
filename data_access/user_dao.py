"""Author: Andrew Kim
"""

from google.cloud.firestore import Transaction, DocumentReference, DocumentSnapshot, CollectionReference, Client, transactional
import google
from typing import Type
from models.user import User
import data_access

CTX = data_access.config.Context

db = CTX.db

class UserDao:
	"""Description
	   Database access object for user
	"""

	def __init__(self, client: Client):
		self.client = Client
		self.userCollectionRef = client.collection(u'Users')

	@transactional
	def getUserWithTransaction(self, transaction: Transaction, userRef: DocumentReference) -> User:
		""" Description
		    Note that this cannot take place if transaction already received write operation
		:type self:
		:param self:

		:type transaction:Transaction:
		:param transaction:Transaction:

		:type userRef:DocumentReference:
		:param userRef:DocumentReference:

		:raises:
		
		:rtype:
		"""

		try:
			snapshot: DocumentSnapshot = userRef.get(transaction=transaction)
			snapshotDict: dict = snapshot.to_dict()
			user = User.fromDict(snapshotDict)
			return user
		except google.cloud.execeptions.NotFound:
			raise Exception('No such document! ' + str(userRef.id))

	def getUser(self, userRef: DocumentReference):
		transaction = db.transaction()
		userResult = self.getUserWithTransaction(transaction, userRef)
		transaction.commit()
		return userResult

	def createUser(self, user: User):
		return self.userCollectionRef.add(user.toDict())

	@transactional
	def addToEventSchedule(self, transaction: Transaction, userRef: str, eventRef: str, toEventRideRequestRef: str):
		userRef: DocumentReference = db.collection(u'users').document(userRef)
		""" Description
			Add a event schedule to users/<userId>/eventSchedule

		Precondition: 


		:type self:
		:param self:
	
		:type transaction:Transaction:
		:param transaction:Transaction:
	
		:type userRef:str:
		:param userRef:str:
	
		:type eventRef:str:
		:param eventRef:str:
	
		:type eventSchedule:dict:
		:param eventSchedule:dict:
	
		:raises:
	
		:rtype:
		"""

		# Get the CollectionReference of the collection that contains EventSchedule's
		eventSchedulesRef: CollectionReference = userRef.collection(u'eventSchedules')
		
		# Retrieve document id to be used as the key
		eventId = DocumentReference(eventRef).id

		# Get the DocumentReference for the EventSchedule
		eventScheduleRef: DocumentReference = eventSchedulesRef.document(eventId)
		transaction.set(eventScheduleRef, {
			'toEventRideRequestRef': toEventRideRequestRef
		}, merge=True) # So that 'fromEventRideRequestRef' is not overwritten

	@transactional
	def setOrbitWithTransaction(self, transaction: Transaction, newUser: User, userRef: DocumentReference):
		transaction.set(userRef, newUser)
