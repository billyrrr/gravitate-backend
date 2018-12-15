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

	def __init__(self, uid, membership, phone_number, display_name, photo_url, pickupAddress):
			""" Description
				This function initializes a User Object.
				Note that this function should not be called directly.
				Note that event schedule is not parsed with this class

				:param self:
				:param uid: String
				:param display_name:String
				:param photo_url: Image
				:param pickupAddress: String
			"""

			self.uid = uid
			self.membership = membership
			self.display_name = display_name
			self.phone_number = phone_number
			self.photo_url = photo_url
			self.pickupAddress = pickupAddress

	def toDict(self):
		userDict = {
			"uid": self.uid,
			"membership": self.membership,
			"display_name": self.display_name,
			"phone_number": self.phone_number,
			"photo_url": self.photo_url,
			"pickupAddress": self.pickupAddress,
		}
		return userDict

	def toFirestoreDict(self):
		userFirestoreDict = {
			'membership': self.membership,
			'pickupAddress': self.pickupAddress
		}
		return userFirestoreDict

	@staticmethod
	def fromDict(userDict):
		""" Description
			This function creates User. 
				(User Factory)

			:param rideRequestDict: 
		"""
		uid = userDict['uid']
		membership = userDict['membership']
		phone_number = userDict['phone_number']
		display_name = userDict['display_name']
		photo_url = userDict['photo_url']
		pickupAddress = userDict['pickupAddress']
		
		return User(uid,membership,phone_number,display_name, photo_url, pickupAddress)