import unittest
from google.cloud import firestore
from models.user import User
from data_access.user_dao import UserDao
import config

db = config.Context.db

userDict: dict = {
    "uid": "testuid1",
    "firstName": "Johnny",
    "lastName": "Appleseed",
    "picture": 100000001,
    "friendList": [],
    "eventSchedule": [],
    'memberships': 'rider'

}

class UserCollectionTest(unittest.TestCase):

    def setUp(self):
        self.user = UserDao().getUserById('SQytDq13q00e0N3H4agR')

    def testAddToEventSchedule(self):
        transaction = db.transaction()
        UserDao().addToEventScheduleWithTransaction(
            transaction, 
            userRef=self.user.getFirestoreRef(), 
            eventRef='/events/testeventid1', 
            toEventRideRequestRef='/rideRequests/testriderequestid1')

class UserDAOTest(unittest.TestCase):

    def setUp(self):
        self.user = User.fromDict(userDict)

    def testCreate(self):
        userRef: firestore.DocumentReference = UserDao().createUser(self.user)
        self.user.setFirestoreRef(userRef)
        print("userRef = {}".format(userRef))