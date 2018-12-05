from models import User
from models import Orbit
from forms.user_creation_form import UserCreationForm
from google.cloud.firestore import DocumentReference, Transaction
from data_access import UserDao
from data_access import EventDao
from firebase_admin import auth

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
        auth.update_user(user.uid,
            phone_number = user.phone_number,
            display_name  = user.display_name,
            photo_url  = user.photo_url,
            disabled = False
        )
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


def getAuthInfo(uid:string, userDict:dict):
    userRecord = auth.get_user(uid)
    userDict["uid"] = userRecord.uid
    userDict["phone_number"] = userRecord.phone_number
    userDict["photo_url"] = userRecord.photo_url
    userDict["display_name"] = userRecord.display_name
    return userDict