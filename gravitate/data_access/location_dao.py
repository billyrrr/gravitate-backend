"""Author: Zixuan Rao, David Nong
"""

from google.cloud.firestore import Transaction, DocumentReference, DocumentSnapshot, CollectionReference, Client, \
    transactional, Query
import google
from typing import Type
from gravitate.models import Location, AirportLocation, UcLocation
import warnings
from gravitate import context
from functools import partial

CTX = context.Context

db = CTX.db


class LocationGenericDao:
    """ Description
        Database access object for ride request

    """

    def __init__(self):
        self.locationCollectionRef = db.collection('locations')

    def get_ref_by_id(self, location_id):
        """
        This method returns location_ref by location_id.
        :param location_id:
        :return:
        """
        return self.locationCollectionRef.document(location_id)

    @staticmethod
    # @transactional
    def get_with_transaction(transaction: Transaction, locationRef: DocumentReference) -> Type[Location]:
        """ Description
            Note that this cannot take place if transaction already received write operations.
            "If a transaction is used and it already has write operations added, this method cannot be used (i.e. read-after-write is not allowed)."

        :type self:
        :param self:

        :type transaction:Transaction:
        :param transaction:Transaction:

        :type locationRef:DocumentReference:
        :param locationRef:DocumentReference:

        :raises:

        :rtype:
        """

        try:
            snapshot: DocumentSnapshot = locationRef.get(
                transaction=transaction)
            snapshotDict: dict = snapshot.to_dict()
            location = Location.from_dict(snapshotDict)
            location.set_firestore_ref(locationRef)
            return location
        except google.cloud.exceptions.NotFound:
            raise Exception('No such document! ' + str(locationRef.id))

    def get(self, locationRef: DocumentReference):
        if isinstance(locationRef, str):
            locationRef = str_to_ref(locationRef)
        snapshot: DocumentSnapshot = locationRef.get()
        snapshotDict: dict = snapshot.to_dict()
        location = Location.from_dict(snapshotDict)
        location.set_firestore_ref(locationRef)
        return location
        return locationResult

    def set(self, location, location_ref: DocumentReference):
        location_ref.set(location.to_dict())

    def find_by_airport_code(self, airportCode) -> AirportLocation:
        query: Query = self.locationCollectionRef.where(
            'airportCode', '==', airportCode)
        airportLocations = list()
        docs = query.get()
        for doc in docs:
            airportLocationDict = doc.to_dict()
            airportLocation = AirportLocation.from_dict(airportLocationDict)
            airportLocation.set_firestore_ref(doc.reference)
            airportLocations.append(airportLocation)
        if len(airportLocations) != 1:
            warnings.warn("Airport Location that has the airport code is not unique or does not exist: {}".format(
                airportLocations))
            return None

        result = airportLocations.pop()
        return result

    def find_by_campus_code(self, campusCode) -> UcLocation:
        query: Query = self.locationCollectionRef.where(
            'campusCode', '==', campusCode)
        airportLocations = list()
        docs = query.get()
        for doc in docs:
            airportLocationDict = doc.to_dict()
            airportLocation = AirportLocation.from_dict(airportLocationDict)
            airportLocation.set_firestore_ref(doc.reference)
            airportLocations.append(airportLocation)
        if len(airportLocations) != 1:
            warnings.warn("Airport Location that has the airport code is not unique or does not exist: {}".format(
                airportLocations))
            return None

        result = airportLocations.pop()
        return result

    def query(self, airportCode, terminal) -> Location:
        # TODO implement
        pass

    def insert_new(self, location: Type[Location]) -> DocumentReference:
        """ Description
        :type self:
        :param self:

        :type location:Type[Location]:
        :param location:Type[Location]:

        :raises:

        :rtype:
        """
        _, locationRef = self.locationCollectionRef.add(location.to_dict())
        return locationRef

    def delete(self, singleLocationRef: DocumentReference):
        """ Description
            This function deletes a ride request from the database

        :type self:
        :param self:

        :type singleLocationRef:DocumentReference:
        :param singleLocationRef:DocumentReference:

        :raises:

        :rtype:
        """
        return singleLocationRef.delete()


    @staticmethod
    def _set_with_transaction(transaction: Transaction, newLocation: Type[Location], locationRef: DocumentReference):
        return transaction.set(locationRef, newLocation)

    @staticmethod
    def set_with_transaction_new(transaction: Transaction, newLocation: Type[Location], locationRef: DocumentReference):
        step = partial(LocationGenericDao._set_with_transaction(), newLocation=newLocation, locationRef=locationRef)
        return step(transaction)


    @staticmethod
    @transactional
    def set_with_transaction_transactional(transaction: Transaction, newLocation: Type[Location], locationRef: DocumentReference):
        """ Description
            Note that a read action must have taken place before anything is set with that transaction.

        :type self:
        :param self:

        :type transaction:Transaction:
        :param transaction:Transaction:

        :type newLocation:Type[Location]:
        :param newLocation:Type[Location]:

        :type locationRef:DocumentReference:
        :param locationRef:DocumentReference:

        :raises:

        :rtype:
        """
        locationDict = newLocation.to_dict()
        return transaction.set(locationRef, locationDict)

    @staticmethod
    def set_with_transaction(transaction: Transaction, newLocation: Type[Location], locationRef: DocumentReference):
        """ Description
            Note that a read action must have taken place before anything is set with that transaction.

        :type self:
        :param self:

        :type transaction:Transaction:
        :param transaction:Transaction:

        :type newLocation:Type[Location]:
        :param newLocation:Type[Location]:

        :type locationRef:DocumentReference:
        :param locationRef:DocumentReference:

        :raises:

        :rtype:
        """
        locationDict = newLocation.to_dict()
        return transaction.set(locationRef, locationDict)


def str_to_ref(ref_str: str):
    k = ref_str.split("/")
    if k[0] == "":
        k.pop(0)
    return db.document("/".join(k))
