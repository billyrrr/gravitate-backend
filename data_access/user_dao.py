"""Author: Andrew Kim
"""

from google.cloud.firestore import Transaction, DocumentReference, DocumentSnapshot, CollectionReference, Client, transactional
import google
from typing import Type
from models.user import User

class UserDao:
	"""Description
	   Database access object for user
	"""

	def __init__(self, client: Client):
		self.client = Client
		self.orbitCollectionRef = client.collection(u'Users')

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
			user = User(snapshotDict)
			return user
		except google.cloud.execeptions.NotFound:
			raise Exception('No such document! ' + str(userRef.id))

	def getUser(self, userRef: DocumentReference):
		transaction = self.client.transaction()
		userResult = self.getUserWithTransaction(transaction, userRef)
		transaction.commit()
		return userResult

	def createUser(self, user: User):
		return self.userCollectionRef.add(user.toDict())

	@transactional
	def setOrbitWithTransaction(self, transaction: Transaction, newUser: User, userRef: DocumentReference):
		transaction.set(userRef, newUser)
