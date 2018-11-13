"""Author: Zixuan Rao
"""

from google.cloud.firestore import Transaction, DocumentReference, DocumentSnapshot, CollectionReference, Client, transactional
from models.ride_request import RideRequest, AirportRideRequest, SocialEventRideRequest
import google
from typing import Type
from main import db as dbClientRideRequestDao

class RideRequestGenericDao:
    """ Description	
        Database access object for ride request

    """

    def __init__(self):
        self.rideRequestCollectionRef = dbClientRideRequestDao.collection('RideRequests')

    @transactional
    def getRideRequestWithTransaction(self, transaction: Transaction, rideRequestRef: DocumentReference) -> Type[RideRequest]:
        """ Description
            Note that this cannot take place if transaction already received write operations. 
            "If a transaction is used and it already has write operations added, this method cannot be used (i.e. read-after-write is not allowed)."

        :type self:
        :param self:

        :type transaction:Transaction:
        :param transaction:Transaction:

        :type rideRequestRef:DocumentReference:
        :param rideRequestRef:DocumentReference:

        :raises:

        :rtype:
        """

        try:
            snapshot: DocumentSnapshot = rideRequestRef.get(
                transaction=transaction)
            snapshotDict: dict = snapshot.to_dict()
            rideRequest = RideRequest.fromDict(snapshotDict)
            return rideRequest
        except google.cloud.exceptions.NotFound:
            raise Exception('No such document! ' + str(rideRequestRef.id))

    def getRideRequest(self, rideRequestRef: DocumentReference):
        transaction = dbClientRideRequestDao.transaction()
        rideRequestResult = self.getRideRequestWithTransaction(
            transaction, rideRequestRef)
        transaction.commit()
        return rideRequestResult

    def createRideRequest(self, rideRequest: Type[RideRequest]):
        """ Description
        :type self:
        :param self:

        :type rideRequest:Type[RideRequest]:
        :param rideRequest:Type[RideRequest]:

        :raises:

        :rtype:
        """
        return self.rideRequestCollectionRef.add(rideRequest.toDict())

    def deleteRideRequest(self, singleRideRequestRef: DocumentReference):
        """ Description
            This function deletes a ride request from the database

        :type self:
        :param self:

        :type singleRideRequestRef:DocumentReference:
        :param singleRideRequestRef:DocumentReference:

        :raises:

        :rtype:
        """
        return singleRideRequestRef.delete()

    @transactional
    @staticmethod
    def setRideRequestWithTransaction(transaction: Transaction, newRideRequest: Type[RideRequest], rideRequestRef: DocumentReference):
        """ Description
            Note that a read action must have taken place before anything is set with that transaction. 

        :type self:
        :param self:

        :type transaction:Transaction:
        :param transaction:Transaction:

        :type newRideRequest:Type[RideRequest]:
        :param newRideRequest:Type[RideRequest]:

        :type rideRequestRef:DocumentReference:
        :param rideRequestRef:DocumentReference:

        :raises:

        :rtype:
        """
        return transaction.set(rideRequestRef, newRideRequest)
