from models.ride_request import RideRequest
from models.orbit import Orbit
#places RideRequest into the Orbit
#only works if orbit's orbitId, orbitCategory, and eventId is already instantiated
def placeInOrbit(r = RideRequest(), o = Orbit()):
	#set RideRequest's requestCompletion to true
	r.requestCompletion = True

	#RideRequest's orbitRef no longer null and references Orbit's documentReference
	r.orbitRef = getFirestoreRef(o) 
	
	#create a ticket to insert into userTicketPairs
	ticket = {
		'rideRequestRef': getFirestoreRef(r)
		'userWillDrive': False
		'hasCheckedIn': False
		'inChat': True
		'pickupAddress': r.pickupAddress
	}
	
	#insert in to orbit's userTicketPair	
	o.userTicketPairs.append(ticket)
	
	#done
	return None
	

