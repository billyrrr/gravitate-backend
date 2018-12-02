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

	def __init__(self, uid, memberships, firstName, lastName, picture, friendList):
			""" Description
				This function initializes a User Object.
				Note that this function should not be called directly.
				Note that event schedule is not parsed with this class

				:param self:
				:param uid: String
				:param firstName: String
				:param lastName: String
				:param picture: Image
				:param friendList: List of Users
			"""

			self.uid = uid
			self.memberships = memberships
			self.firstName = firstName
			self.lastName = lastName
			self.picture = picture
			self.friendList = friendList

	def toDict(self):
		userDict = {
			'uid': self.uid,
			'memberships': self.memberships,
			'firstName': self.firstName,
			'lastName': self.lastName,
			'picture': self.picture,
			'friendList': self.friendList,
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
		
		return User(uid,memberships,firstName,lastName,picture,friendList)