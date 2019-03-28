import random
import string

from google.cloud.firestore import Transaction

from gravitate.controllers import fireauthutils
from gravitate.data_access import UserDao


# Generate a random string 
# with 32 characters. 
# https://www.geeksforgeeks.org/generating-random-ids-python/
def randomId():
    randomIdStr = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
    return randomIdStr


def saveUser(user, transaction: Transaction = None):
    if user.get_firestore_ref():
        if transaction is None:
            raise Exception('transaction is not provided. ')
        UserDao().set_user_with_transaction(transaction, user, user.get_firestore_ref())
        fireauthutils.update_user(user)

    else:
        newRef = UserDao().create_user(user)
        user.set_firestore_ref(newRef)


# Do we need 1 for each thing that needs to be changed?
# Name, Contact Email, Phone, Address
def editUser(user, transaction: Transaction = None):
    if user.get_firestore_ref():
        if transaction is None:
            raise Exception('transaction is not provided.')
    else:
        UserDao().get_user_by_id(user.userId)


def getUser(uid: string):
    UserDao().get_user_by_id(uid)
