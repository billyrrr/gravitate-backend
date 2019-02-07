from google.cloud import firestore
# from google.cloud.firestore import Transaction, DocumentReference, DocumentSnapshot, CollectionReference, Client, transactional


class DocumentReference(firestore.DocumentReference):
    pass


class DocumentSnapshot(firestore.DocumentSnapshot):
    pass


class Transaction(firestore.Transaction):
    pass


class CollectionReference(firestore.CollectionReference):
    pass


class Client(firestore.Client):
    pass


class Transaction(firestore.Transaction):
    pass


transactional = firestore.transactional
