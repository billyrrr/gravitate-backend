from models.user import User
from models.orbit import Orbit
from forms.user_creation_form import UserCreationForm
from google.cloud.firestore import DocumentReference, Transaction
from data_access.user_dao import UserDao
from data_access.event_dao import EventDao

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