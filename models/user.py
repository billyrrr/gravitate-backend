"""Author: Andrew Kim
"""

from google.cloud.firestore import DocumentReference

#user class
class User(object):
	""" Description
	this class represents the user object
	"""
	
	__firestoreRef: DocumentReference = None

	def setFirestoreRef(self, firestoreRef: str):
		self.__firestoreRef = firestoreRef

	def getFirestoreRef(self):
		return self.__firestoreRef

