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


class UsersCollectionTest(unittest.TestCase):

    def setUp(self):
        self.user = User.fromDict(userDict)

    def testAddToEventSchedule(self):
        # TODO Implement
        pass

class UsersDAOTest(unittest.TestCase):

    def setUp(self):
        self.user = User.fromDict(userDict)

    def testCreate(self):
        userRef = UserDao().createUser(self.user)
        print("userRef = {}".format(userRef))