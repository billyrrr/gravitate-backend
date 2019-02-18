import gravitate.main as main
from flask.testing import FlaskClient

from unittest import TestCase
import json
from test import context

db = context.Context.db
firebaseApp = context.Context.firebaseApp

userId = 'SQytDq13q00e0N3H4agR'

cred = context.Context._cred


def getMockAuthHeaders(uid="testuid1"):
    # user = auth.get_user(uid)
    # userIdToken = user.tokens_valid_after_timestamp
    # # userIdToken = auth.create_custom_token(uid=uid, app=firebaseApp)
    # userIdTokenMock = userIdToken
    # warnings.warn("Note that userIdTokenMock is temporary and the test may fail when the token is no longer valid.")
    userIdTokenMock = uid  # For mocking decoding token as uid
    headers = {'Authorization': userIdTokenMock}
    return headers

#
# # Populate database for uc/campus location and events
# populate_locations.doWorkUc("UCSB")
# populate_airport_events.populate_events(start_string="2018-12-20T08:00:00.000", num_days=15, event_category="campus")

# Populate database for airport location and events
# class ScriptTempTestCase(TestCase):
#
#     def testNothing(self):
#         # populate_locations.doWork()
#         populate_airport_events.populate_events(start_string="2019-01-22T08:00:00.000", num_days=30)

class MainAppTestCase(TestCase):
    app: FlaskClient = None

    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()

    def testAuth(self):
        userIdMock = "1GFLeGxBaaUvudqh3XYbFv2sRHx2"
        mockHeaders = getMockAuthHeaders(uid=userIdMock)
        r = self.app.post(path='/endpointTest', json=json.dumps({'testAuth': True}), headers=mockHeaders)
        responseDict: dict = json.loads(r.data)
        uid = responseDict['uid']
        self.assertEqual(uid, userIdMock)


class MockFormTargetOnly:

    def __init__(self):
        self.earliest = "2018-12-17T09:00:00.000"
        self.latest = "2018-12-17T11:00:00.000"
        self.toEvent = True
