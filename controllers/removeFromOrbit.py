import config
from data_access import OrbitDao
from google.cloud.firestore import DocumentReference, Client
from models.orbit import Orbit
from models.user import User
db = config.Context.db

def removeFromOrbit(orbitRef: DocumentReference, userRef: DocumentReference):
	#remove userRef from orbitRef's userTicketPairs
	orbitDao = OrbitDao()
	userTicketPairs = orbitDao.get(orbitRef).userTicketPairs
	#search userTicketPairs for userRef, remove userRef and corresponding ticket once done
	for user, ticket in userTicketPairs:
		if user == userRef:
			userTicketPairs.remove(user, ticket)
	

