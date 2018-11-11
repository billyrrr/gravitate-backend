"""Author: Zixuan Rao
"""

from google.cloud.firestore import Transaction, DocumentReference, DocumentSnapshot, CollectionReference, Client, transactional
from models.ride_request import RideRequest
import google


class RideRequestDao:
    """ Description	
        Database access object for ride request

    """

    def __init__(self, client: Client):
        self.client = client
        self.rideRequestCollectionRef = client.collection(u'RideRequests')

    @transactional
    def getRideRequestWithTransaction(self, transaction: Transaction, rideRequestRef: DocumentReference) -> RideRequest:
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
            rideRequest = RideRequest(snapshotDict)
            return rideRequest
        except google.cloud.exceptions.NotFound:
            raise Exception('No such document! ' + str(rideRequestRef.id))

    def getRideRequest(self, rideRequestRef: DocumentReference):
        transaction = self.client.transaction()
        rideRequestResult = self.getRideRequestWithTransaction(
            transaction, rideRequestRef)
        transaction.commit()
        return rideRequestResult

    def createRideRequest(self, rideRequest: RideRequest):
        return self.rideRequestCollectionRef.add(rideRequest.toDict())

    @transactional
    def setRideRequestWithTransaction(self, transaction: Transaction, newRideRequest: RideRequest, rideRequestRef: DocumentReference):
        transaction.set(rideRequestRef, newRideRequest)
