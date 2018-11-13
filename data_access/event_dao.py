"""Author: Zixuan Rao
"""

from google.cloud.firestore import Transaction, DocumentReference, DocumentSnapshot, CollectionReference, Client, transactional
from models.ride_request import RideRequest, AirportRideRequest, SocialEventRideRequest
import google
from typing import Type


class EventGenericDao:
    """ Description	
        Database access object for ride request

    """

    def __init__(self, client: Client):
        self.client = client
        self.rideRequestCollectionRef = client.collection('events')

    def locateAirportEvent(self, timestamp):
        # self.rideRequestCollectionRef.
        # TODO implement a logic to locate the appropriate airport event
        return 