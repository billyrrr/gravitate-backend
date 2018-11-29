"""Author: Zixuan Rao, David Nong
"""

from google.cloud.firestore import Transaction, DocumentReference, DocumentSnapshot, CollectionReference, Client, transactional
from models.event import Event
import google
import config
from typing import Type

db = config.Context.db


# The maximum amount of time where a user can request a ride
# Hard coded to be 1 day in seconds
timeDifference = 24*60*60

class EventDao:
    """ Description	
        Database access object for events

    """
    def locateAirportEvent(self, timestamp):
        """ Description
            Uses the timestamp of an event to find the event reference
        """



        # Grab all of the events in the db
        eventDocs = self.eventCollectionRef.get()


        # Loop through each rideRequest
        for doc in eventDocs:
            # Check if the event is in a valid time frame
            if doc.eventRef.startTimeStamp < (timestamp - timeDifference) and doc.eventRef.endTimeStamp > (timestamp
                - timeDifference):
                return doc.eventRef.id

        return
        

    def __init__(self):
        self.eventCollectionRef = db.collection('events')

    def create(self, event: Event)->DocumentReference:
        _, eventRef = self.eventCollectionRef.add(event.toDict())
        return eventRef
