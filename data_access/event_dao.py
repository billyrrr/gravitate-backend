"""Author: Zixuan Rao, David Nong
"""

from google.cloud.firestore import Transaction, DocumentReference, DocumentSnapshot, CollectionReference, Client, transactional
from models.ride_request import RideRequest, AirportRideRequest, SocialEventRideRequest
import google
from typing import Type

class EventGenericDao:
    """ Description	
        Database access object for events

    """
    def __init__(self, client: Client):
        self.client = client
        self.rideRequestCollectionRef = client.collection('rideRequests')

    def locateAirportEvent(self, timestamp):
        """ Description
            Uses the timestamp of an event to find the event reference
        """

        # Grab all of the events in the db
        eventDocs = self.rideRequestCollectionRef.get()


        # Loop through each rideRequest
        for doc in eventDocs:
            # Check if the event is in a valid time frame
            if doc.eventRef.startTimeStamp < (timestamp - timeDifference) and doc.eventRef.endTimeStamp > (timestamp
                - timeDifference):
                return doc.eventRef.id

        # If there are no valid events
        return None


    
    
    # The maximum amount of time where a user can request a ride
        # Hard coded to be 1 day in seconds
        timeDifference = 86400    
        
