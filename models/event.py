"""Author: Andrew Kim
"""

from google.cloud.firestore import DocumentReference

#event class
class Event(object):
	""" Description
	this class represents the event object
	"""
	
	__firestoreRef: DocumentReference = None
	
	def setFirestoreRef(self, firestoreRef: str):
		self.__firestoreRef = firestoreRef

	def getFirestoreRef(self):
		return self.__firestoreref

