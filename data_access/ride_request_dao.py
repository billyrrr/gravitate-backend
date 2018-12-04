"""Author: Zixuan Rao
"""

from google.cloud.firestore import Transaction, DocumentReference, DocumentSnapshot, CollectionReference, Client, transactional
import google
from typing import Type
from models.ride_request import RideRequest, AirportRideRequest
import config

CTX = config.Context

db = CTX.db

class RideRequestGenericDao:
    """ Description	
        Database access object for ride request

    """

    def __init__(self):
        self.rideRequestCollectionRef = db.collection('rideRequests')

    def getIds(self, isRequestCompletionFalse = False):
        """ Description
            Get the ids of RideRequests
        
        :type self:
        :param self:
    
        :type isRequestCompletionFalse:
        :param isRequestCompletionFalse: If set to true, only RideRequests with requestCompletion=False will be returned. 
    
        :raises:
    
        :rtype:
        """

        docIds = list()
    
        if isRequestCompletionFalse:
            docs = self.rideRequestCollectionRef.where("requestCompletion", "==", False).get()
        else:
            docs = self.rideRequestCollectionRef.get()
        for doc in docs:
            docId = doc.id
            docIds.append(docId)
        return docIds

    @staticmethod
    @transactional
    def getRideRequestWithTransaction(transaction: Transaction, rideRequestRef: DocumentReference) -> Type[RideRequest]:
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
        transaction = db.transaction()
        rideRequestResult = self.getRideRequestWithTransaction(
            transaction, rideRequestRef)
        transaction.commit()
        return rideRequestResult

    def createRideRequest(self, rideRequest: Type[RideRequest])->DocumentReference:
        """ Description
        :type self:
        :param self:

        :type rideRequest:Type[RideRequest]:
        :param rideRequest:Type[RideRequest]:

        :raises:

        :rtype:
        """
        _, rideRequestRef = self.rideRequestCollectionRef.add(rideRequest.toDict())
        return rideRequestRef

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

    @staticmethod
    @transactional
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
        return transaction.set(rideRequestRef, newRideRequest.toDict())

    # @transactional
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
