import unittest
from google.cloud import firestore
from models.user import User
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


# class UsersCollectionTest(unittest.TestCase):

#     def setUp(self):
#         self.user = User.fromDict(userDict)

#     def testAddToEventSchedule(self):
#         # TODO Implement
#         pass
