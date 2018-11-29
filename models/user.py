from google.cloud.firestore import DocumentReference

# user class


class User(object):
	""" Description
	this class represents the user object
	"""

	__firestoreRef: DocumentReference = None

	def setFirestoreRef(self, firestoreRef: str):
		self.__firestoreRef = firestoreRef

	def getFirestoreRef(self):
		return self.__firestoreRef

	def __init__(self, uid, memberships, firstName, lastName, picture, friendList, eventSchedule):
			""" Description
				This function initializes a User Object.
				Note that this function should not be called directly.

				:param self:
				:param uid: String
				:param firstName: String
				:param lastName: String
				:param picture: Image
				:param friendList: List of Users
				:param eventSchedule: List of Events
			"""

			self.uid = uid
			self.memberships = memberships
			self.firstName = firstName
			self.lastName = lastName
			self.picture = picture
			self.friendList = friendList
			self.eventSchedule = eventSchedule

	def toDict(self):
		userDict = {
			'uid': self.uid,
			'memberships': self.memberships,
			'firstName': self.firstName,
			'lastName': self.lastName,
			'picture': self.picture,
			'friendList': self.friendList,
			'eventSchedule': self.eventSchedule
		}
		return userDict

	@staticmethod
	def fromDict(userDict):
		""" Description
			This function creates User. 
				(User Factory)

			:param rideRequestDict: 
		"""
		uid = userDict['uid']
		memberships = userDict['memberships']
		firstName = userDict['firstName']
		lastName = userDict['lastName']
		picture = userDict['picture']
		friendList = userDict['friendList']
		eventSchedule = userDict['eventSchedule']
		
		return User(uid,memberships,firstName,lastName,picture,friendList,eventSchedule)

eventScheduleKey = "testeventid1" 
eventScheduleValueExample = {
	'rideStatus': True,
	'toEventRideRequestRef': '/rideRequests/testriderequestref1',
	# 'fromEventRideRequestRef': '/rideRequests/testriderequestref2'
	# key reserved for MVP++
}