import json
from unittest import TestCase, skip

from firebase_admin import auth
from flask.testing import FlaskClient

from gravitate import main as main
from gravitate import context


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


@skip("Comment this skip when you run the test")
class UserNotificationTest(TestCase):
    """
    For now, try running each test independently, since the test setUp and tearDown may
        not work as expected and can affect device group.
    """

    app: FlaskClient = None

    def setUp(self):
        """
        Creates a new user
        """
        main.app.testing = True
        self.app = main.app.test_client()
        auth.create_user(app=context.Context.firebaseApp, uid=test_user1_dict["uid"])
        path = '/users/' + test_user1_dict["uid"]
        r = self.app.post(path=path, json=json.dumps(test_user1_dict))
        assert r.status_code == 200

    def tearDown(self):
        """
        Deletes the user created in the test setUp.
        """
        auth.delete_user(app=context.Context.firebaseApp, uid=test_user1_dict["uid"])

    def test_authentication(self):
        """
        Tests that unauthenticated requests returns 403 Unauthorized and does not change any settings.
        This can be skipped for now.
        """
        pass

    def test_turn_on_one(self):
        """
        Tests that when user turns on notification on an installation, the server turns on notifications
            for it. That is, when sending a notification to the user, the device will now receive notifications.
        """
        path = '/users/' + test_user1_dict["uid"] + '/notifications'
        # Calls UPDATE/PATCH on "/users/example_user_id/notifications"
        r = self.app.patch(path=path, json={
            # Turn on notifications for client installation with registration ID: registrationId1
            "registrationId1": True
        })

    def test_turn_off_one(self):
        """
        Tests that when user turns off notification on an installation, the server turns off notifications
            for it. That is, when sending a notification to the user, the device will no longer receive
            notifications. (Precondition: the user has turned on notifications for the device previously)
        """
        # TODO: implement test
        pass

    def test_get_all_devices(self):
        """
        Tests that the server returns a list of all devices and their off/on state for notifications.
        """
        # TODO: add missing setup steps
        path = '/users/' + test_user1_dict["uid"] + '/notifications'
        # Calls GET on "/users/example_user_id/notifications"
        r = self.app.get(path=path)
        d = r.json
        self.assertDictEqual(d, {
            "registrationId1": True,
            "registrationId2": False
        })

    def test_delete_all_notifications(self):
        """
        Tests that the server disables/deletes all notifications for all devices associated with a userId.
        """
        # Calls DELETE on "/users/example_user_id/notifications"
        path = '/users/' + test_user1_dict["uid"] + '/notifications'
        r = self.app.delete(path=path)

        # Calls GET on "/users/example_user_id/notifications"
        path = '/users/' + test_user1_dict["uid"] + '/notifications'
        r = self.app.get(path=path)
        d = r.json
        self.assertDictEqual(d, {}, "service should return an empty dict after all registration IDs"
                                    " are deleted")
