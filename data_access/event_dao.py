"""Author: Zixuan Rao
"""

from google.cloud.firestore import Transaction, DocumentReference, DocumentSnapshot, CollectionReference, Client, transactional
from models.event import Event
import google
import config
from typing import Type

db = config.Context.db


class EventDao:
    """ Description	
        Database access object for ride request

    """

    def __init__(self):
        self.eventCollectionRef = db.collection('events')

    def locateAirportEvent(self, timestamp):
        # self.rideRequestCollectionRef.
        # TODO implement a logic to locate the appropriate airport event
        return 

    def create(self, event: Event)->DocumentReference:
        _, eventRef = self.eventCollectionRef.add(event.toDict())
        return eventRef
