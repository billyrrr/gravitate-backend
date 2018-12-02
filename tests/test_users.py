import main_user

from flask.testing import FlaskClient
from flask import request, jsonify

import unittest
from google.cloud import firestore
from firebase_admin import auth

from models.user import User
from data_access.user_dao import UserDao
import json
import config

db = config.Context.db

userDict: dict = {
    'uid': 'Ep7WCjZatagd1Nr50ToNkIp4WWt2',
    'phoneNumber': '908-655-6098',
    'membership': 'rider',
    'displayName': 'Johnny Appleseed',
    'photoURL': 'abcdefhijkl.com'
}

# userDict: dict = {
#     uid: "testuidLeon1",
#     phoneNumber: "908-655-6098",
#     membership: "rider",
#     fullName: "Johnny Appleseed",
#     photoURL: "abcdefhijkl.com"
# }

class UserEndPointTest(unittest.TestCase):

    app: FlaskClient = None

    def setUp(self):

        main_user.app.testing = True
        self.app = main_user.app.test_client()

    def testCreateUser(self):
        r = self.app.post(path='/users', json = json.dumps(userDict))
        assert r.status_code == 200
        # assert 'Hello World' in r.data.decode('utf-8')

class UserCollectionTest(unittest.TestCase):

    def setUp(self):
        self.user = UserDao().getUserById('SQytDq13q00e0N3H4agR')

    def testAddToEventSchedule(self):
        transaction = db.transaction()
        UserDao().addToEventScheduleWithTransaction(
            transaction, 
            userRef=self.user.getFirestoreRef(), 
            eventRef=db.document('events', 'testeventid1'), 
            toEventRideRequestRef=db.document('rideRequests', 'testriderequestid1'))

class UserDAOTest(unittest.TestCase):

    def setUp(self):
        self.user = User.fromDict(userDict)

    def testCreate(self):
        userRef: firestore.DocumentReference = UserDao().createUser(self.user)
        self.user.setFirestoreRef(userRef)
        print("userRef = {}".format(userRef))

"""     def testGet(self):
        userWithEventSchedules = UserDao().getUserById('SQytDq13q00e0N3H4agR') """
        

class FirebaseUserTest(unittest.TestCase):
    def testGetFirebaseInfo(self):
        user = auth.get_user("LwkGgNe7HMRpFn6v9kcYCL7HBpx1")
        print(user.display_name)

    def testDeleteUser(self):
        auth.delete_user("LwkGgNe7HMRpFn6v9kcYCL7HBpx1")

    def testUpdateUser(self):
        auth.update_user("Ep7WCjZatagd1Nr50ToNkIp4WWt2",
            phone_number = "+14155552671",
            display_name = "David Nong",
            disabled = False
        )