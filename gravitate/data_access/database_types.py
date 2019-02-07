from typing import Type, Union, TypeVar, Any
from google.cloud import firestore
from google.cloud import datastore


Reference = TypeVar("Reference", firestore.DocumentReference, datastore.Key)

class DataReference:

    def __init__(self, reference: Reference):
        self._reference_type = None
        self._firestore_reference = None
        self._datastore_key = None

        self._set_reference(reference)

    def _get_reference(self):
        if issubclass(self._reference_type, firestore.DocumentReference):
            return self._firestore_reference
        elif issubclass(self._reference_type, datastore.Key):
            return self._datastore_key
        else:
            raise ValueError("type(reference) returns {}".format(str(self._reference_type)))

    def _set_reference(self, reference:  Reference):
        if issubclass(type(reference), firestore.DocumentReference):
            self._reference_type = firestore.DocumentReference
            self._firestore_reference = reference
        elif issubclass(type(reference), datastore.Key):
            self._reference_type = datastore.Key
            self._datastore_key = reference
        else:
            raise ValueError("type(reference) returns {}".format(str(type(reference))))
