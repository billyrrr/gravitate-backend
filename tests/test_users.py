import unittest
from usersHelper.users import addToEventSchedule
from google.cloud import firestore

class UsersCollectionTest(unittest.TestCase):
    def setUp(self):
        self.db = firestore.Client()
    def testAddToEventSchedule(self):
        db = self.db
        addToEventSchedule(db, 'test_uid_1', {'foo': 'bar'})