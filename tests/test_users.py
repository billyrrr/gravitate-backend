import main_user

from flask.testing import FlaskClient
from flask import request, jsonify

from unittest import TestCase
from google.cloud import firestore
from firebase_admin import auth

from models import User
from data_access import UserDao
import json

import config

db = config.Context.db

userDict: dict = {
    'uid': 'Ep7WCjZatagd1Nr50ToNkIp4WWt2',
    'phone_number': '+17777777777',
    'membership': 'rider',
    'display_name': 'Leon Wu',
    'photo_url': 'https://www.gstatic.com/webp/gallery/1.jpg'
}

# userDict: dict = {
#     uid: "testuidLeon1",
#     phoneNumber: "908-655-6098",
#     membership: "rider",
#     fullName: "Johnny Appleseed",
#     photoURL: "abcdefhijkl.com"
# }

class UserEndPointTest(TestCase):

    app: FlaskClient = None

    def setUp(self):

        main_user.app.testing = True
        self.app = main_user.app.test_client()

    def testGetUser(self):
        path = '/users/' + userDict["uid"]
        r = self.app.get(path=path)
        # assert r.status_code == 200
        print(r.status_code)

    def testCreateUser(self):
        path = '/users/' + userDict["uid"]
        r = self.app.post(path=path, json = json.dumps(userDict))
        assert r.status_code == 200
        # assert 'Hello World' in r.data.decode('utf-8')

class UserCollectionTest(TestCase):

    def setUp(self):
        self.user = UserDao().getUserById('SQytDq13q00e0N3H4agR')

    # def testAddToEventSchedule(self):
    #     transaction = db.transaction()
    #     UserDao().addToEventScheduleWithTransaction(
    #         transaction, 
    #         userRef=self.user.getFirestoreRef(), 
    #         eventRef=db.document('events', 'testeventid1'), 
    #         toEventRideRequestRef=db.document('rideRequests', 'testriderequestid1'))

class UserDAOTest(TestCase):

    def setUp(self):
        self.user = User.fromDict(userDict)

    def testCreate(self):
        userRef: firestore.DocumentReference = UserDao().createUser(self.user)
        self.user.setFirestoreRef(userRef)
        print("userRef = {}".format(userRef))

    def testGetUserId(self):
        user = UserDao().getUserById(userDict["uid"])
        self.assertEquals(userDict['display_name'], user.display_name)
        

class FirebaseUserTest(TestCase):
    def testGetFirebaseInfo(self):
        user = auth.get_user("Ep7WCjZatagd1Nr50ToNkIp4WWt2")
        print(user.display_name)

    # def testDeleteUser(self):
    #     auth.delete_user("LwkGgNe7HMRpFn6v9kcYCL7HBpx1")

    def testUpdateUser(self):
        auth.update_user("JTKWXo5HZkab9dqQbaOaqHiSNDH2",
            phone_number = "+17777777877",
            display_name = "David Nong",
            disabled = False
        )

class FirestoreUserTest(TestCase):

    def testUserCollectionExists(self):
        uid = "Ep7WCjZatagd1Nr50ToNkIp4WWt2"
        user = UserDao().getUserById(uid)
        self.assertEqual(user.uid, userDict["uid"])
        self.assertEqual(user.membership, userDict["membership"])
        self.assertEqual(user.phone_number, userDict["phone_number"])
        self.assertEqual(user.photo_url, userDict["photo_url"])
        self.assertEqual(user.display_name, userDict["display_name"])
