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

def saveUser(User, transaction: Transaction = None):
    if (User.getFirestoreRef()):
        if not transaction:
            raise Exception('transaction is not provided. ')
            UserDao.setUserWithTransaction(transaction, User, User.getFirestoreRef())
    else:
        newRef = UserDao().createUser(User)
        User.setFirestoreRef(newRef)