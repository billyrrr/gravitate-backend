from gravitate.models import User, Orbit
from gravitate.forms.user_creation_form import UserCreationForm
from google.cloud.firestore import DocumentReference, Transaction
from gravitate.data_access import UserDao, EventDao
from gravitate.controllers import fireauthutils

import random 
import string 
  
# Generate a random string 
# with 32 characters. 
# https://www.geeksforgeeks.org/generating-random-ids-python/
def randomId():
    randomIdStr = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]) 
    return randomIdStr

def saveUser(user, transaction: Transaction = None):
    if (user.getFirestoreRef()):
        if not transaction:
            raise Exception('transaction is not provided. ')
        UserDao().setUserWithTransaction(transaction, user, user.getFirestoreRef())
        fireauthutils.update_user(user)

    else:
        newRef = UserDao().createUser(user)
        user.setFirestoreRef(newRef)


# Do we need 1 for each thing that needs to be changed?
        #Name, Contact Email, Phone, Address 
def editUser(user, transaction: Transaction = None):
    if (user.getFirestoreRef()):
        if not transaction:
            raise Exception('transaction is not provided.')
    else:
        UserDao().getUserById(user.userId)

def getUser(uid:string):
    UserDao().getUserById(uid)

