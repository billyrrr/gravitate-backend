from models.ride_request import RideRequest
from models.orbit import Orbit
#places RideRequest into the Orbit
#only works if orbit's orbitId, orbitCategory, and eventId is already instantiated
def placeInOrbit(r = RideRequest(), o = Orbit()):
	#set RideRequest's requestCompletion to true
	r.dictionary["requestCompletion"] = True

	#RideRequest's orbitId no longer null and references Orbit's oId
	r.dictionary["orbitId"] = o.dictionary["oId"]

	#insert in to orbit's userTicketPairs	
	o.dictionary["userTicketPairs"].append(r.ticket)
	
	#return dictionaries
	return r.dictionary, o.dictionary

