from models.ride_request import RideRequest
from models.orbit import Orbit 
#places RideRequest into the Orbit
#only works if orbit's orbitId, orbitCategory, and eventId is already instantiated
def placeInOrbit(r = RideRequest(), o = Orbit()):
	#set RideRequest's requestCompletion to true
	r.dictionary[requestCompletion] = True

	#RideRequest's orbitId no longer null and references Orbit's oId
	r.dictionary[orbitId] = o.dictionary[oId]

	#fill in ticket and insert in to orbit's userTicketPairs
	d = r.dictionary
	ticket = o.Ticket{ "rideRequestId": d[rId], "userWillDrive": d[driverStatus], "hasCheckedIn": d[hasCheckedIn], "inChat": True, "pickupAdress": d[pickupAddress] }
	o.dictionary[userTicketPairs].append(ticket)
	return r.dictionary, o.dictionary

	# TODO: change the method to adapt to new RideRequest and Orbit object structure
	# TODO: change rideRequest.dictionary to rideRequest