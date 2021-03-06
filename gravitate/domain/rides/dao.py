"""Author: Zixuan Rao
"""

from typing import Type

import google
from google.cloud.firestore import Transaction, DocumentReference, DocumentSnapshot

from gravitate import context
from . import RideRequest
from gravitate.data_access import utils

CTX = context.Context

db = CTX.db


class RideRequestGenericDao:
    """ Description	
        Database access object for ride request

    """

    def __init__(self):
        self.rideRequestCollectionRef = db.collection('rideRequests')

    def get_ids(self, incomplete=False):
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

    def get_by_user(self, userId):
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
    def get_with_transaction(transaction: Transaction, rideRequestRef: DocumentReference) -> Type[RideRequest]:
        """ Description Note that this cannot take place if transaction already received write operations. "If a
        transaction is used and it already has write operations added, this method cannot be used (i.e.
        read-after-write is not allowed)."

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

    def ref_from_id(self, rid: str):
        return self.rideRequestCollectionRef.document(rid)

    def get_by_id(self, rid: str):
        ref = self.ref_from_id(rid)
        ride_request = self.get(ref)
        return ride_request

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
        rideRequestId = utils.random_id()
        rideRequestRef = RideRequestGenericDao(
        ).rideRequestCollectionRef.document(document_id=rideRequestId)
        rideRequest.set_firestore_ref(rideRequestRef)
        return rideRequest

    def set(self, rideRequest: Type[RideRequest]) -> DocumentReference:
        rideRequest.get_firestore_ref().set(rideRequest.to_dict())

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
    def set_with_transaction(transaction: Transaction, newRideRequest: Type[RideRequest],
                             rideRequestRef: DocumentReference):
        """ Description
            Note that a read action must have taken place before anything is set with that transaction. 

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

