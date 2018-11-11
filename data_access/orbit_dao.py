"""Author: Zixuan Rao
"""

from google.cloud.firestore import Transaction, DocumentReference, DocumentSnapshot, CollectionReference, Client, transactional
from models.orbit import Orbit
import google


class OrbitDao:
    """ Description	
        Database access object for ride request

    """

    def __init__(self, client: Client):
        self.client = client
        self.orbitCollectionRef = client.collection(u'Orbits')

    @transactional
    def getOrbitWithTransaction(self, transaction: Transaction, orbitRef: DocumentReference) -> Orbit:
        """ Description
            Note that this cannot take place if transaction already received write operations. 
            "If a transaction is used and it already has write operations added, this method cannot be used (i.e. read-after-write is not allowed)."

        :type self:
        :param self:

        :type transaction:Transaction:
        :param transaction:Transaction:

        :type orbitRef:DocumentReference:
        :param orbitRef:DocumentReference:

        :raises:

        :rtype:
        """

        try:
            snapshot: DocumentSnapshot = orbitRef.get(
                transaction=transaction)
            snapshotDict: dict = snapshot.to_dict()
            orbit = Orbit(snapshotDict)
            return orbit
        except google.cloud.exceptions.NotFound:
            raise Exception('No such document! ' + str(orbitRef.id))

    def getOrbit(self, orbitRef: DocumentReference):
        transaction = self.client.transaction()
        orbitResult = self.getOrbitWithTransaction(
            transaction, orbitRef)
        transaction.commit()
        return orbitResult

    def createOrbit(self, orbit: Orbit):
        return self.orbitCollectionRef.add(orbit.toDict())

    @transactional
    def setOrbitWithTransaction(self, transaction: Transaction,
                                      newOrbit: Orbit, orbitRef: DocumentReference):
        transaction.set(orbitRef, newOrbit)
