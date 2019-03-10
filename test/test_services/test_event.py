from gravitate import main as main
from gravitate.domain.event.models import Event
from gravitate.domain.event.dao import EventDao
import unittest
from google.cloud import firestore
from test.store import getEventDict
from test.test_main import getMockAuthHeaders
from test.test_services.utils import _create_ride_requests_for_tests


class EventServiceTest(unittest.TestCase):

    def setUp(self):
        event_dict = getEventDict(use_firestore_ref=True)
        self.event = Event.from_dict(event_dict)
        self.refs_to_delete = list()

        main.app.testing = True
        self.app = main.app.test_client()
        self.userId = "testuid1"

        event_ref: firestore.DocumentReference = EventDao().create(self.event)
        self.event.set_firestore_ref(event_ref)
        self.refs_to_delete.append(event_ref)
        self.event_id = event_ref.id

    def testGet(self):
        r = self.app.get(path='/events' + '/' + self.event_id,
                         headers=getMockAuthHeaders()
                         )

        dict_expected = {
            'eventCategory': "airport",
            'participants': [],
            'eventLocation': "LAX",
            'eventEarliestArrival': "2018-12-17T00:00:00",
            'eventLatestArrival': "2018-12-17T23:59:59",
            'pricing': 100,
            'locationId': "testairportlocationid1",
            'isClosed': False
        }

        result = dict(r.json)

        self.assertEqual(r.status_code, 200, "GET is successful")
        self.assertDictEqual(dict_expected, result)

    def tearDown(self):
        for ref in self.refs_to_delete:
            ref.delete()
        self.refs_to_delete.clear()

