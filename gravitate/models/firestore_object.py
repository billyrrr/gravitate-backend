from google.cloud.firestore_v1beta1 import DocumentReference


class FirestoreObject(object):
    __firestoreRef: DocumentReference = None

    def __init__(self):
        pass

    def setFirestoreRef(self, firestoreRef: str):
        self.__firestoreRef = firestoreRef

    def getFirestoreRef(self):
        return self.__firestoreRef