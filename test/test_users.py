import json
from unittest import TestCase

from firebase_admin import auth
from flask.testing import FlaskClient
from google.cloud import firestore

from gravitate import main as main
from gravitate.data_access import UserDao
from gravitate.models import User
from test import context


test_user1_dict: dict = {
    'uid': 'testuserid1',
    'phone_number': '+17777777777',
    'membership': 'rider',
    'display_name': 'Leon Wu',
    'photo_url': 'https://www.gstatic.com/webp/gallery/1.jpg',
    'pickupAddress': 'UCSD'
}

test_user2_dict: dict = {
    'uid': 'testuserid2',
    'phone_number': '+17777777778',
    'membership': 'rider',
    'display_name': 'User Two',
    'photo_url': 'https://www.gstatic.com/webp/gallery/2.jpg',
    'pickupAddress': 'UCSD'
}

userDict = test_user1_dict


class UserEndPointTest(TestCase):
    app: FlaskClient = None

    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()
        context.auth.create_user(app=context.Context.firebaseApp, uid = test_user1_dict["uid"])
        path = '/users/' + test_user1_dict["uid"]
        r = self.app.post(path=path, json=json.dumps(test_user1_dict))
        assert r.status_code == 200

    def tearDown(self):
        context.auth.delete_user(app=context.Context.firebaseApp, uid=test_user1_dict["uid"])

    def testGetUser(self):
        path = '/users/' + test_user1_dict["uid"]
        r = self.app.get(path=path)
        # assert r.status_code == 200
        print(r.status_code)


class UserCreationEndpointTest(TestCase):

    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()
        context.auth.create_user(app=context.Context.firebaseApp, uid=test_user2_dict["uid"])

    def tearDown(self):
        context.auth.delete_user(app=context.Context.firebaseApp, uid=test_user2_dict["uid"])

    def testCreateUser(self):
        path = '/users/' + test_user2_dict["uid"]
        r = self.app.post(path=path, json=json.dumps(test_user2_dict))
        assert r.status_code == 200
        # assert 'Hello World' in r.data.decode('utf-8')


class UserCollectionTest(TestCase):

    def setUp(self):
        self.user = UserDao().get_user_by_id('SQytDq13q00e0N3H4agR')

    # def testAddToEventSchedule(self):
    #     transaction = db.transaction()
    #     UserDao().add_to_event_schedule_with_transaction(
    #         transaction,
    #         userRef=self.user.get_firestore_ref(),
    #         eventRef=db.document('events', 'testeventid1'),
    #         toEventRideRequestRef=db.document('rideRequests', 'testriderequestid1'))


class UserDAOTest(TestCase):

    def setUp(self):
        self.user = User.from_dict(userDict)

    def testCreate(self):
        userRef: firestore.DocumentReference = UserDao().create_user(self.user)
        self.user.set_firestore_ref(userRef)
        print("userRef = {}".format(userRef))

    def testCreateTempTesting(self):
        userRef: firestore.DocumentReference = UserDao().create_user(self.user)
        self.user.set_firestore_ref(userRef)
        print("userRef = {}".format(userRef))


class UserDAOTestGet(TestCase):

    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()
        context.auth.create_user(app=context.Context.firebaseApp, uid=test_user1_dict["uid"])
        path = '/users/' + test_user1_dict["uid"]
        r = self.app.post(path=path, json=json.dumps(test_user1_dict))
        assert r.status_code == 200

    def tearDown(self):
        context.auth.delete_user(app=context.Context.firebaseApp, uid=test_user1_dict["uid"])

    def testGetUser(self):
        uid = userDict["uid"]
        user = UserDao().get_user_by_id(uid)
        print(user.to_dict())

    def testGetUserId(self):
        user = UserDao().get_user_by_id(userDict["uid"])
        self.assertEquals(userDict['display_name'], user.display_name)
        self.assertEquals(userDict['phone_number'], user.phone_number)
        self.assertEquals(userDict['uid'], user.uid)
        self.assertEquals(userDict['membership'], user.membership)
        self.assertEquals(userDict['photo_url'], user.photo_url)
        self.assertEquals(userDict['pickupAddress'], user.pickupAddress)


class FirebaseUserTest(TestCase):

    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()
        context.auth.create_user(app=context.Context.firebaseApp, uid=test_user1_dict["uid"])
        path = '/users/' + test_user1_dict["uid"]
        r = self.app.post(path=path, json=json.dumps(test_user1_dict))
        assert r.status_code == 200

    def tearDown(self):
        context.auth.delete_user(app=context.Context.firebaseApp, uid=test_user1_dict["uid"])

    def testGetFirebaseInfo(self):
        user = auth.get_user(userDict["uid"], app=context.Context.firebaseApp)
        print(user.display_name)

    # def testDeleteUser(self):
    #     auth.delete_user("LwkGgNe7HMRpFn6v9kcYCL7HBpx1")
    # Note that the code needs to be adapted to specify app = config.Context.firebase App

    def testUpdateUser(self):
        auth.update_user(userDict["uid"],
                         phone_number="+17777777779",
                         display_name="Zixuan Rao",
                         disabled=False,
                         app=context.Context.firebaseApp
                         )
        user = UserDao().get_user_by_id(userDict["uid"])
        self.assertEquals("Zixuan Rao", user.display_name)
        self.assertEquals("+17777777779", user.phone_number)
        self.assertEquals(userDict['uid'], user.uid)
        self.assertEquals(userDict['membership'], user.membership)
        self.assertEquals(userDict['photo_url'], user.photo_url)
        self.assertEquals(userDict['pickupAddress'], user.pickupAddress)


class FirestoreUserTest(TestCase):

    def testUserCollectionExists(self):
        uid = "1GFLeGxBaaUvudqh3XYbFv2sRHx2"
        user = UserDao().get_user_by_id(uid)
        self.assertEqual(user.uid, userDict["uid"])
        self.assertEqual(user.membership, userDict["membership"])
        self.assertEqual(user.phone_number, userDict["phone_number"])
        self.assertEqual(user.photo_url, userDict["photo_url"])
        self.assertEqual(user.display_name, userDict["display_name"])
        self.assertEqual(user.pickupAddress, userDict["pickupAddress"])

        print(json.dumps(user.to_dict()))

