import unittest

from google.cloud import firestore

from gravitate.data_access import EventDao
from gravitate.models import Event
from test.store import eventDict
from gravitate import context
from test import scripts as setup_scripts

CTX = context.Context

db = CTX.db

class EventDAOTest(unittest.TestCase):

    def setUp(self):
        self.event = Event.from_dict(eventDict)
        self.refs_to_delete = list()

        self.cl = setup_scripts.SetUpTestDatabase()
        self.cl.clear_before()

        self.pl = setup_scripts.scripts.populate_locations.PopulateLocationCommand()
        self.refs_to_delete.extend(self.pl.execute())

    def testCreate(self):
        eventRef: firestore.DocumentReference = EventDao().create(self.event)
        self.event.set_firestore_ref(eventRef)
        print("eventRef = {}".format(eventRef))

    # def testDelete(self):
    # 	eventRef: firestore.DocumentReference = EventDao().create(self.event)
    # 	self.event.set_firestore_ref(eventRef)
    # 	self.delete(eventRef)
    # 	# self.assertEquals()

    def testGet(self):
        def setUp(self):
            eventRef: firestore.DocumentReference = EventDao().create(self.event)
            self.event.set_firestore_ref(eventRef)
            self.refs_to_delete.append(eventRef)

        setUp(self)
        event: Event = EventDao().get(self.event.get_firestore_ref())
        self.assertIsNotNone(event)

    def testGetStrRef(self):
        def setUp(self):
            eventRef: firestore.DocumentReference = EventDao().create(self.event)
            self.event.set_firestore_ref(eventRef)
            self.refs_to_delete.append(eventRef)

        setUp(self)
        path_str = "/events/" + self.event.get_firestore_ref().id
        event: Event = EventDao().get(path_str)
        self.assertIsNotNone(event)

    def tearDown(self):
        self.cl.clear_after()
        for ref in self.refs_to_delete:
            ref.delete()
        self.refs_to_delete.clear()

    def testFindByTimestamp(self):

        def setUp(self):
            eventRef: firestore.DocumentReference = EventDao().create(self.event)
            self.event.set_firestore_ref(eventRef)
            self.refs_to_delete.append(eventRef)
        setUp(self)

        # Monday, December 17, 2018 3:00:00 PM GMT-08:00 = 1545087600
        event: Event = EventDao().find_by_timestamp(1545087600, category="airport")
        self.assertNotEqual(None, event)

        # self.assertEquals(event.startTimestamp, 1546502400)
        # self.assertEquals("BxPBnrl6kItoNc6x0NqO", event.get_firestore_ref().id)
