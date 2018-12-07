"""Author: Zixuan Rao, David Nong
"""

from google.cloud.firestore import Transaction, DocumentReference, DocumentSnapshot, CollectionReference, Client, transactional, Query
import google
from typing import Type
from models.location import Location, AirportLocation
import warnings
import config

CTX = config.Context

db = CTX.db


class LocationGenericDao:
	""" Description	
		Database access object for ride request

	"""

	def __init__(self):
		self.locationCollectionRef = db.collection('locations')

	@staticmethod
	@transactional
	def getWithTransaction(transaction: Transaction, locationRef: DocumentReference) -> Type[Location]:
		""" Description
			Note that this cannot take place if transaction already received write operations. 
			"If a transaction is used and it already has write operations added, this method cannot be used (i.e. read-after-write is not allowed)."

		:type self:
		:param self:

		:type transaction:Transaction:
		:param transaction:Transaction:

		:type locationRef:DocumentReference:
		:param locationRef:DocumentReference:

		:raises:

		:rtype:
		"""

		try:
			snapshot: DocumentSnapshot = locationRef.get(
				transaction=transaction)
			snapshotDict: dict = snapshot.to_dict()
			location = Location.fromDict(snapshotDict)
			location.setFirestoreRef(locationRef)
			return location
		except google.cloud.exceptions.NotFound:
			raise Exception('No such document! ' + str(locationRef.id))

	def get(self, locationRef: DocumentReference):
		transaction = db.transaction()
		locationResult = self.getWithTransaction(
			transaction, locationRef)
		transaction.commit()
		return locationResult

	def findByAirportCode(self, airportCode) -> AirportLocation:
		query: Query = self.locationCollectionRef.where(
			'airportCode', '==', airportCode)
		airportLocations = list()
		docs = query.get()
		for doc in docs:
			airportLocationDict = doc.to_dict()
			airportLocation = AirportLocation.fromDict(airportLocationDict)
			airportLocation.setFirestoreRef(doc.reference)
			airportLocations.append(airportLocation)
		if len(airportLocations)!= 1:
			warnings.warn("Airport Location that has the airport code is not unique or does not exist: {}".format(
				airportLocations))
			return None

		result = airportLocations.pop()
		return result

	def query(self, airportCode, terminal) -> Location:
		# TODO implement
		pass

	def create(self, location: Type[Location])->DocumentReference:
		""" Description
		:type self:
		:param self:

		:type location:Type[Location]:
		:param location:Type[Location]:

		:raises:

		:rtype:
		"""
		_, locationRef = self.locationCollectionRef.add(location.toDict())
		return locationRef

	def delete(self, singleLocationRef: DocumentReference):
		""" Description
			This function deletes a ride request from the database

		:type self:
		:param self:

		:type singleLocationRef:DocumentReference:
		:param singleLocationRef:DocumentReference:

		:raises:

		:rtype:
		"""
		return singleLocationRef.delete()

	@transactional
	@staticmethod
	def setWithTransaction(transaction: Transaction, newLocation: Type[Location], locationRef: DocumentReference):
		""" Description
			Note that a read action must have taken place before anything is set with that transaction. 

		:type self:
		:param self:

		:type transaction:Transaction:
		:param transaction:Transaction:

		:type newLocation:Type[Location]:
		:param newLocation:Type[Location]:

		:type locationRef:DocumentReference:
		:param locationRef:DocumentReference:

		:raises:

		:rtype:
		"""
		return transaction.set(locationRef, newLocation)
