from google.cloud.firestore import Transaction, DocumentReference, DocumentSnapshot, CollectionReference, Client, \
    transactional

import google
from typing import Type
from gravitate.models import User, AirportEventSchedule

# from config import auth

import string
import warnings
from gravitate import context

CTX = context.Context
auth = context.auth

db = CTX.db


# TODO remove transactional and add test

def _get_auth_info(uid: string, userDict: dict):
    userRecord = auth.get_user(uid, app=CTX.firebaseApp)
    userDict["uid"] = userRecord.uid
    userDict["phone_number"] = userRecord.phone_number
    userDict["photo_url"] = userRecord.photo_url
    userDict["email"] = userRecord.email
    userDict["display_name"] = userRecord.display_name
    return userDict


class UserDao:
    """Description
       Database access object for user
        # TODO delete object.set_firestore_ref()
    """

    def __init__(self):
        self.userCollectionRef = db.collection(u'users')

    @staticmethod
    def user_exists(userRef: DocumentReference):
        snapshot: DocumentSnapshot = userRef.get()
        if snapshot.exists:
            return True
        else:
            return False

    def user_id_exists(self, userId: str):
        userRef = self.userCollectionRef.document(userId)
        return self.user_exists(userRef)

    def get_ref(self, userId: str) -> DocumentReference:
        ref: DocumentReference = self.userCollectionRef.document(userId)
        return ref

    @staticmethod
    @transactional
    def get_user_with_transaction(transaction, userRef: DocumentReference):
        """ Description
            Note that this cannot take place if transaction already received write operation
        :type self:
        :param self:
        :type transaction:Transaction:
        :param transaction:Transaction:
        :type userRef:DocumentReference:
        :param userRef:DocumentReference:
        :raises:
        :rtype:
        """

        userExists = UserDao.user_exists(userRef)

        if userExists:
            snapshot = userRef.get(transaction=transaction)
            userDict = snapshot.to_dict()
            _get_auth_info(userRef.id, userDict)
            user = User.from_dict(userDict)
            user.set_firestore_ref(userRef)
            return user
        else:
            return None
        # except google.cloud.exceptions.NotFound:
        #     raise Exception('No such document! ' + str(userRef.id))
        # except:
        # return None

    def get_user(self, userRef: DocumentReference):
        transaction = db.transaction()
        userResult = self.get_user_with_transaction(transaction, userRef)
        if (userResult != None):
            userResult.set_firestore_ref(userRef)
            transaction.commit()
            return userResult
        else:
            return None

    def get_user_by_id(self, userId: str):
        userRef = self.userCollectionRef.document(userId)
        user = self.get_user(userRef)
        return user

    def get_by_id_with_transaction(self, transaction: Transaction, userId: str) -> User:
        userRef = self.userCollectionRef.document(userId)
        user = self.get_user_with_transaction(transaction, userRef)
        return user

    def create_user(self, user: User):
        userRef = self.userCollectionRef.add(user.to_dict())
        return userRef

    def update_fcm_token(self, userId: str, token):
        userRef: DocumentReference = self.userCollectionRef.document(userId)
        deltaDict = {
            "fcmToken": token
        }
        userRef.update(deltaDict)
        return

    def get_fcm_token(self, userId: str):
        userRef: DocumentReference = self.userCollectionRef.document(userId)
        userSnapshot: DocumentSnapshot = userRef.get()
        userData = userSnapshot.to_dict()
        fcmToken = userData["fcmToken"]
        return fcmToken

    @staticmethod
    @transactional
    def set_user_with_transaction(transaction: Transaction, newUser: Type[User], userRef: DocumentReference):
        transaction.set(userRef, newUser.to_firestore_dict())

    @staticmethod
    def remove_event_schedule_with_transaction(transaction: Transaction, userRef: DocumentReference = None,
                                               orbitId: str = None):
        eventScheduleRef: DocumentReference = userRef.collection("eventSchedules").document(orbitId)
        transaction.delete(eventScheduleRef)

    @staticmethod
    # @transactional
    def add_to_event_schedule_with_transaction(transaction: Transaction, userRef: str = None,
                                               eventRef: DocumentReference = None, eventSchedule: AirportEventSchedule = None):
        """ Description
                Add a event schedule to users/<userId>/eventSchedule
				Note that the toEventRideRequestRef will be 
					overwritten without warning if already set. 
					(Same for fromEventRideRequestRef.) 
        :type self:
        :param self:
        :type transaction:Transaction:
        :param transaction:Transaction:
        :type userRef:str:
        :param userRef:str:
        :type eventRef:str:
        :param eventRef:str:
        :type eventSchedule:dict:
        :param eventSchedule:dict:
        :raises:
        :rtype:
        """

        # userRef: DocumentReference = db.collection(u'users').document(userRef)

        # Get the CollectionReference of the collection that contains AirportEventSchedule's
        eventSchedulesRef: CollectionReference = userRef.collection(
            u'eventSchedules')

        # Retrieve document id to be used as the key
        eventId = eventRef.id
        # eventId = 'testeventid1'
        # warnings.warn("Using mock/test event id. Must replace before release. ")

        # Get the DocumentReference for the AirportEventSchedule
        eventScheduleRef: DocumentReference = eventSchedulesRef.document(eventId)
        eventScheduleDict = eventSchedule.to_dict()
        transaction.set(eventScheduleRef, eventScheduleDict,
                        merge=True)  # So that 'fromEventRideRequestRef' is not overwritten

    def set_with_transaction(self, transaction: Transaction, newUser: User, userRef: DocumentReference):
        transaction.set(userRef, newUser)
