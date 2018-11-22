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
	@staticmethod
	def fromDictAndReference(eventDict, eventRef):
		event = Event.fromDict(eventDict)
		event.setFirestoreRef(eventRef)
		return event

	def fromDict(eventDict):
		""" Description
		    This function creates an event
		    
		    :param eventDict:
		"""
		eventRef = eventDict['eventRef']
		eventCategory = eventDict['eventCategory']
		participants = eventDict['particapants']
		eventLocation = eventDict['eventLocation']
		startTimeStamp = eventDict['startTimeStamp']
		endTimeStamp = eventDict['endTimeStamp']
		pricing = eventDict['pricing']
		return Event(eventRef, eventCategory, participants, eventLocation, startTimeStamp, endTimeStamp, pricing)

	def toDict(self):
		eventDict = {
			'eventRef' = self.eventRef
			'eventCategory' = self.eventCategory
			'participants' = self.participants
			'eventLocation' = self.eventLocation
			'startTimeStamp' = self.startTimeStamp
			'endTimeStamp' = self.endTimeStamp
			'pricing' = self.pricing
		}
		return eventDict

	def __init__(self, eventRef, eventCategory, participants, eventLocation, startTimeStamp, endTimeStamp, pricing):
		"""Description
		   This function initializes an Event object

		   :param self:
		   :param eventRef:
		   :param eventCategory:
		   :param participants:
		   :param eventLocation:
		   :param startTimeStamp:
		   :param endTimeStamp:
		   :param pricing:
		"""
		self.eventRef = eventRef
		self.eventCategory = eventCategory
		self.participants = participants
		self.eventLocation = eventLocation
		self.startTimeStamp = startTimeStamp
		self.endTimeStamp = endTimeStamp
		self.pricing = pricing
