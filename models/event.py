"""Author: Andrew Kim
"""

from google.cloud.firestore import DocumentReference

#event class
class Event(object):
	""" Description
	this class represents the event object
		Note that reference to the object eventRef is deprecated. 
		Get and set firestoreRef instead. 

	"""
	
	__firestoreRef: DocumentReference = None
	
	def setFirestoreRef(self, firestoreRef: str):
		self.__firestoreRef = firestoreRef

	def getFirestoreRef(self):
		return self.__firestoreRef
	
	@staticmethod
	def fromDictAndReference(eventDict, eventRef):
		event = Event.fromDict(eventDict)
		event.setFirestoreRef(eventRef)
		return event

	@staticmethod
	def fromDict(eventDict):
		""" Description
		    This function creates an event
		    
		    :param eventDict:
		"""
		eventCategory = eventDict['eventCategory']
		participants = eventDict['participants']
		eventLocation = eventDict['eventLocation']
		startTimestamp = eventDict['startTimestamp']
		endTimestamp = eventDict['endTimestamp']
		pricing = eventDict['pricing']
		locationRefs = eventDict['locationRefs']
		return Event(eventCategory, participants, eventLocation, startTimestamp, endTimestamp, pricing, locationRefs)

	def toDict(self):
		eventDict = {
			'eventCategory': self.eventCategory,
			'participants': self.participants,
			'eventLocation': self.eventLocation,
			'startTimestamp': self.startTimestamp,
			'endTimestamp': self.endTimestamp,
			'pricing': self.pricing,
			'locationRefs': self.locationRefs
		}
		return eventDict

	def __init__(self, eventCategory, participants, eventLocation, startTimestamp, endTimestamp, pricing, locationRefs):
		"""Description
		   This function initializes an Event object

		   :param self:
		   :param eventCategory:
		   :param participants:
		   :param eventLocation:
		   :param startTimestamp:
		   :param endTimestamp:
		   :param pricing:
		   :param locationRefs: a list of locationRef that corresponds to this event
		"""
		self.eventCategory = eventCategory
		self.participants = participants
		self.eventLocation = eventLocation
		self.startTimestamp = startTimestamp
		self.endTimestamp = endTimestamp
		self.pricing = pricing
		self.locationRefs = locationRefs
