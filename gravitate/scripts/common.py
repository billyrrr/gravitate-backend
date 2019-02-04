from gravitate.context import Context
from google.cloud.firestore import DocumentReference, CollectionReference
import warnings

db = Context.db

def _delete_all(collection_name):
    app_name = Context.firebaseApp.name
    if not app_name.find("testing"):
        raise Exception("Firebase App Name is {}. Only app name containing testing is supported".format(app_name))
    event_collection: CollectionReference = db.collection(collection_name)

    warnings.warn("Deleting collection: {}, App Name: {}.".format(collection_name, app_name))

    def delete_collection(coll_ref, batch_size, doc_limit=10):
        """
        Ref: https://firebase.google.com/docs/firestore/manage-data/delete-data
        :param coll_ref:
        :param batch_size:
        :return:
        """
        docs = coll_ref.limit(doc_limit).get()
        deleted = 0
        docs_count = 0

        for doc in docs:
            docs_count = docs_count + 1
            print(u'Deleting doc {} => {}'.format(doc.id, doc.to_dict()))
            doc.reference.delete()
            deleted = deleted + 1

        if deleted < batch_size and docs_count >= doc_limit:  # Note that this line was "if deleted >= batch_size"
            return delete_collection(coll_ref, batch_size)

    delete_collection(event_collection, 100)


def delete_all_events():
    _delete_all("events")


def delete_all_locations():
    _delete_all("locations")
