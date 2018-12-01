"""Author: Andrew Kim
"""

from google.cloud.firestore import Transaction, DocumentReference, DocumentSnapshot, CollectionReference, Client, transactional
import google
from typing import Type
from models.user import User
import data_access
import warnings

CTX = data_access.config.Context

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
    def getUserWithTransaction(transaction, userRef):
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

        try:
            snapshot: DocumentSnapshot = userRef.get(transaction=transaction)
            snapshotDict: dict = snapshot.to_dict()
            user = User.fromDict(snapshotDict)
            return user
        except google.cloud.exceptions.NotFound:
            raise Exception('No such document! ' + str(userRef.id))

    def getUser(self, userRef: DocumentReference):
        transaction = db.transaction()
        userResult = self.getUserWithTransaction(transaction, userRef)
        userResult.setFirestoreRef(userRef)
        transaction.commit()
        return userResult

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
    """         print(newUser)
            print(newUser.toDict()) """
        return transaction.set(userRef, User.toDict())