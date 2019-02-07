"""
Author: Zixuan Rao

TODO: implement

"""

from typing import Type, Union, TypeVar, Any
import google
from google.cloud import firestore
from google.cloud import datastore
from gravitate.models.firestore_object import FirestoreObject

Reference = TypeVar("Reference", firestore.DocumentReference, datastore.Key)


def _is_firestore_document_reference(reference_type) -> bool:
    """ Return true if type is firestore DocumentReference.

    :param reference_type: type(obj) only
    :return:
    """
    return issubclass(reference_type, firestore.DocumentReference)


def _is_datastore_entity_key(reference_type) -> bool:
    """ Return true if type is datastore Key.

    :param reference_type: type(obj) only
    :return:
    """
    return issubclass(reference_type, datastore.Key)


class DataReference:

    def __init__(self, reference: Reference):
        self._reference_type = None
        self._firestore_reference: firestore.DocumentReference = None
        self._datastore_key: datastore.Key = None

        self._set_reference(reference)

    @property
    def id(self):
        if _is_firestore_document_reference(self._reference_type):
            return self._firestore_reference.id
        elif _is_datastore_entity_key(self._reference_type):
            return self._datastore_key.id

    def get_firestore_ref(self) -> firestore.DocumentReference:
        """ Return firestore DocumentReference

        :return:
        """
        return self._get_reference()

    def _get_reference(self):
        if _is_firestore_document_reference(self._reference_type):
            return self._firestore_reference
        elif _is_datastore_entity_key(self._reference_type):
            return self._datastore_key
        else:
            raise ValueError("type(reference) returns {}".format(str(self._reference_type)))

    def _set_reference(self, reference:  Reference):
        if _is_firestore_document_reference(type(reference)):
            self._reference_type = firestore.DocumentReference
            self._firestore_reference = reference
        elif _is_datastore_entity_key(type(reference)):
            self._reference_type = datastore.Key
            self._datastore_key = reference
        else:
            raise ValueError("type(reference) returns {}".format(str(type(reference))))


class DataAccessObject:
    """ Description
        Database access object

    """

    @staticmethod
    def get_with_transaction(transaction: firestore.Transaction, ref: DataReference, obj_class: Type[FirestoreObject]):
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

        firestore_document_ref = ref.get_firestore_ref()

        try:
            snapshot: firestore.DocumentSnapshot = firestore_document_ref.get(
                transaction=transaction)
            snapshotDict: dict = snapshot.to_dict()
            obj = obj_class.from_dict(snapshotDict)
            obj.set_firestore_ref(firestore_document_ref)
            return obj
        except google.cloud.exceptions.NotFound:
            raise Exception('No such document! ' + str(firestore_document_ref.id))

    def get(self, ref: DataReference, obj_class: Type[FirestoreObject] ):
        firestore_document_ref = ref.get_firestore_ref()
        snapshot: firestore.DocumentSnapshot = firestore_document_ref.get()
        snapshotDict: dict = snapshot.to_dict()
        rideRequest = obj_class.from_dict(snapshotDict)
        rideRequest.set_firestore_ref(firestore_document_ref)
        return rideRequest

    def ref_from_id(self, rid: str):
        """ Returns DataReference from id
        TODO: implement

        :param rid:
        :return:
        """
        # return self.rideRequestCollectionRef.document(rid)
        raise NotImplementedError

    def get_by_id(self, rid: str):
        """ Returns object from id
        TODO: implement

        :param rid:
        :return:
        """
        # ref = self.ref_from_id(rid)
        # ride_request = self.get(ref)
        # return ride_request
        raise NotImplementedError

    def create(self, obj: Type[FirestoreObject]) -> Type[FirestoreObject]:
        """ Description
            This method sets the firestoreRef of the object.
            Note that the object is not saved to database with this method.

            TODO: implement

        :type self:
        :param self:
        :type rideRequest:Type[RideRequest]:
        :param rideRequest:Type[RideRequest]:

        :raises:

        :rtype:
        """
        # rideRequestId = utils.random_id()
        # rideRequestRef = RideRequestGenericDao(
        # ).rideRequestCollectionRef.document(document_id=rideRequestId)
        # print(rideRequestRef)
        # rideRequest.set_firestore_ref(rideRequestRef)
        # return rideRequest
        raise NotImplementedError

    def set(self, obj: Type[FirestoreObject]) -> DataReference:
        """ Set an object without a transaction
            TODO: implement

        :param obj:
        :return:
        """
        # rideRequest.get_firestore_ref().set(rideRequest.to_dict())
        raise NotImplementedError

    def delete(self, ref: DataReference):
        """ Description
            This function deletes an object from the database

        :type self:
        :param self:

        :type singleRideRequestRef:DocumentReference:
        :param singleRideRequestRef:DocumentReference:

        :raises:

        :rtype:
        """
        # return singleRideRequestRef.delete()
        raise NotImplementedError

    @staticmethod
    # @transactional
    def set_with_transaction(transaction: Transaction, obj: Type[FirestoreObject],
                             ref: DataReference):
        """ Description
            Note that a read action must have taken place before anything is set with that transaction.

            TODO: implement

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
        # return transaction.set(rideRequestRef, newRideRequest.to_dict())
        raise NotImplementedError
