from google.cloud.firestore import Transaction, DocumentReference, DocumentSnapshot, CollectionReference, Client, transactional

import google
from typing import Type
from models.user import User
from models.event_schedule import EventSchedule
from controllers.userutils import getAuthInfo

from firebase_admin import auth

import data_access
import warnings
import config

CTX = config.Context

db = CTX.db


class UserDao:
    """Description
       Database access object for user
        # TODO delete object.setFirestoreRef()
    """

    def __init__(self):
        self.userCollectionRef = db.collection(u'users')

    @staticmethod
    @transactional
    def getUserWithTransaction(transaction, userRef: DocumentReference):
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

        # try:

        snapshot: DocumentSnapshot = userRef.get(transaction=transaction)
        if snapshot.exists:
            snapshotDict: dict = snapshot.to_dict()
            userDict = getAuthInfo(userRef.id, snapshotDict)
            user = User.fromDict(userDict)
            return user
        else:
            return None
        # except google.cloud.exceptions.NotFound:
        #     raise Exception('No such document! ' + str(userRef.id))
        # except:
            # return None

    # def checkUserById(self, userId: str):
    #     userRef = self.userCollectionRef.document(userId)
    #     try:
    #         userRef.get()
    #         return True
    #     except:
    #         return False


    def getUser(self, userRef: DocumentReference):
        transaction = db.transaction()
        userResult = self.getUserWithTransaction(transaction, userRef)
        if ( userResult != None ):
            userResult.setFirestoreRef(userRef)
            transaction.commit()
            return userResult
        else:
            return None

    def getUserById(self, userId: str):
        userRef = self.userCollectionRef.document(userId)
        user = self.getUser(userRef)
        return user

    def createUser(self, user: User):
        userRef = self.userCollectionRef.add(user.toDict())
        return userRef

    @staticmethod
    @transactional
    def setUserWithTransaction(transaction: Transaction, newUser: Type[User], userRef: DocumentReference):
        transaction.set(userRef, newUser.toFirestoreDict())

    @staticmethod
    @transactional
    def addToEventScheduleWithTransaction(transaction: Transaction, userRef: str=None, eventRef: DocumentReference=None, eventSchedule: EventSchedule=None):
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

        # Get the CollectionReference of the collection that contains EventSchedule's
        eventSchedulesRef: CollectionReference = userRef.collection(
            u'eventSchedules')

        # Retrieve document id to be used as the key
        eventId = eventRef.id
        # eventId = 'testeventid1'
        # warnings.warn("Using mock/test event id. Must replace before release. ")

        # Get the DocumentReference for the EventSchedule
        eventScheduleRef: DocumentReference = eventSchedulesRef.document(eventId)
        eventScheduleDict = eventSchedule.toDict()
        transaction.set(eventScheduleRef, eventScheduleDict, merge=True)  # So that 'fromEventRideRequestRef' is not overwritten

    @transactional
    def setWithTransaction(self, transaction: Transaction, newUser: User, userRef: DocumentReference):
        transaction.set(userRef, newUser)