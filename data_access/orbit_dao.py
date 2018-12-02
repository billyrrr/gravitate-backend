"""Author: Zixuan Rao
"""

from google.cloud.firestore import Transaction, DocumentReference, DocumentSnapshot, CollectionReference, Client, transactional
from models.orbit import Orbit
import google
import config

db = config.Context.db

class OrbitDao:
    """ Description	
        Database access object for ride request

    """

    def __init__(self):
        self.orbitCollectionRef = db.collection('orbits')

    @staticmethod
    @transactional
    def getOrbitWithTransaction(transaction: Transaction, orbitRef: DocumentReference) -> Orbit:
        """ Description
            Note that this cannot take place if transaction already received write operations. 
            "If a transaction is used and it already has write operations added, this method cannot be used (i.e. read-after-write is not allowed)."

        """

        try:
            snapshot: DocumentSnapshot = orbitRef.get(
                transaction=transaction)
            snapshotDict: dict = snapshot.to_dict()
            orbit = Orbit.fromDict(snapshotDict)
            return orbit
        except google.cloud.exceptions.NotFound:
            raise Exception('No such document! ' + str(orbitRef.id))

    def getOrbit(self, orbitRef: DocumentReference):
        transaction = db.transaction()
        orbitResult = self.getOrbitWithTransaction(
            transaction, orbitRef)
        transaction.commit()
        return orbitResult

    def createOrbit(self, orbit: Orbit)->DocumentReference:
        """ Description
        """
        _, orbitRef = self.orbitCollectionRef.add(orbit.toDict())
        return orbitRef

    def deleteOrbit(self, singleOrbitRef: DocumentReference):
        """ Description
            This function deletes an orbit from the database
            Note that this function should not be called directly from any logics, 
                since you have to delete all references to it from RideRequest, Event, etc. 
        """
        return singleOrbitRef.delete()

    @staticmethod
    @transactional
    def setOrbitWithTransaction(transaction: Transaction, newOrbit: Orbit, orbitRef: DocumentReference):
        """ Description
            Note that a read action must have taken place before anything is set with that transaction. 
        """
        return transaction.set(orbitRef, newOrbit.toDict())
