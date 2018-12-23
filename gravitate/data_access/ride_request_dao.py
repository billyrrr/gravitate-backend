"""Author: Zixuan Rao
"""

from google.cloud.firestore import Transaction, DocumentReference, DocumentSnapshot, CollectionReference, Client, \
    transactional
import google
from typing import Type
from gravitate.models import RideRequest, AirportRideRequest
from gravitate import config

from . import utils

CTX = config.Context

db = CTX.db


class RideRequestGenericDao:
    """ Description	
        Database access object for ride request

    """

    def __init__(self):
        self.rideRequestCollectionRef = db.collection('rideRequests')

    def getIds(self, incomplete=False):
        """ Description
            Get the ids of RideRequests
        
        :type self:
        :param self:
    
        :type incomplete: bool
        :param incomplete: If set to true, only RideRequests with requestCompletion=False will be returned. 
    
        :raises:
    
        :rtype:
        """

        docIds = list()

        if incomplete:
            docs = self.rideRequestCollectionRef.where("requestCompletion", "==", False).get()
        else:
            docs = self.rideRequestCollectionRef.get()
        for doc in docs:
            docId = doc.id
            docIds.append(docId)
        return docIds

    def getByUser(self, userId):
        """ Description
            Returns a list of rideRequests by a user

        :type self:
        :param self:
    
        :type userId:
        :param userId:
    
        :raises:
    
        :rtype: a list of ride requests
        """
        docs = self.rideRequestCollectionRef.where("userId", "==", userId).get()
        rideRequests = list()
        for doc in docs:
            rideRequestDict = doc.to_dict()
            rideRequest = RideRequest.from_dict(rideRequestDict)
            rideRequestRef: DocumentReference = doc.reference
            rideRequest.set_firestore_ref(rideRequestRef)
            rideRequests.append(rideRequest)
        return rideRequests

    @staticmethod
    # @transactional
    def getWithTransaction(transaction: Transaction, rideRequestRef: DocumentReference) -> Type[RideRequest]:
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
            rideRequest = RideRequest.from_dict(snapshotDict)
            rideRequest.set_firestore_ref(rideRequestRef)
            return rideRequest
        except google.cloud.exceptions.NotFound:
            raise Exception('No such document! ' + str(rideRequestRef.id))

    def get(self, rideRequestRef: DocumentReference):
        snapshot: DocumentSnapshot = rideRequestRef.get()
        snapshotDict: dict = snapshot.to_dict()
        rideRequest = RideRequest.from_dict(snapshotDict)
        rideRequest.set_firestore_ref(rideRequestRef)
        return rideRequest


    def create(self, rideRequest: Type[RideRequest]) -> Type[RideRequest]:
        """ Description
            This method sets the firestoreRef of the rideRequest.
            Note that rideRequest is not saved to database with this method.

        :type self:
        :param self:
        :type rideRequest:Type[RideRequest]:
        :param rideRequest:Type[RideRequest]:

        :raises:

        :rtype:
        """
        rideRequestId = utils.randomId()
        rideRequestRef = RideRequestGenericDao(
        ).rideRequestCollectionRef.document(document_id=rideRequestId)
        rideRequest.set_firestore_ref(rideRequestRef)
        return rideRequest

    def delete(self, singleRideRequestRef: DocumentReference):
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

    @staticmethod
    # @transactional
    def setWithTransaction(transaction: Transaction, newRideRequest: Type[RideRequest],
                           rideRequestRef: DocumentReference):
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
        return transaction.set(rideRequestRef, newRideRequest.to_dict())

    # 
    # @staticmethod
    # def setWithTransaction(transaction: Transaction, newEvent: Type[Event], eventRef: DocumentReference):
    #     """ Description
    #         Note that a read action must have taken place before anything is set with that transaction. 

    #     :type self:
    #     :param self:

    #     :type transaction:Transaction:
    #     :param transaction:Transaction:

    #     :type newLocation:Type[Location]:
    #     :param newLocation:Type[Location]:

    #     :type locationRef:DocumentReference:
    #     :param locationRef:DocumentReference:

    #     :raises:

    #     :rtype:
    #     """
    #     return transaction.set(eventRef, eventLocation)
