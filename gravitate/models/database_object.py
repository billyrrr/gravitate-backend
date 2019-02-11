from google.cloud.firestore import DocumentReference
from gravitate.data_access.database_types import DataReference


class DatabaseObject(object):
    __data_reference: DataReference = None

    def __init__(self):
        pass

    def set_reference(self, data_ref: DataReference):
        self.__data_reference = data_ref

    def get_reference(self):
        return self.__data_reference

    @staticmethod
    def from_dict(d):
        raise NotImplementedError("Should be implemented in subclass. ")

    def to_dict(self) -> dict:
        raise NotImplementedError("Should be implemented in subclass. ")
