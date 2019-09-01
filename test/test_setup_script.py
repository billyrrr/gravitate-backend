import unittest

from google.cloud.firestore import CollectionReference

from gravitate import context
from test import scripts as setup_scripts


CTX = context.Context
db = CTX.db


def _count_location_docs():
    location_col_ref: CollectionReference = db.collection("Location")
    all_docs = location_col_ref.get()
    counter = 0
    for _ in all_docs:
        counter += 1
    return counter


def _count_event_docs():
    # TODO: change once switched to flask-boiler
    event_col_ref: CollectionReference = db.collection("events")
    all_docs = event_col_ref.get()
    counter = 0
    for _ in all_docs:
        counter += 1
    return counter


class SetupScriptTest(unittest.TestCase):

    def test_database_operations(self):
        """
        Note that tearDown is not called for this test.
        This test may crush all other tests.
        :return:
        """

        c = setup_scripts.SetUpTestDatabase()

        c.clear_before()  # Clear locations and events collection

        self.assertEqual(_count_location_docs(), 0, "locations collection should be cleared")
        self.assertEqual(_count_event_docs(), 0, "events collection should be cleared")

        c.generate_test_data()  # Generate locations and events needed by a test case

        self.assertNotEqual(_count_location_docs(), 0, "locations collection should have documents")
        self.assertNotEqual(_count_event_docs(), 0, "events collection should have documents")

        c.clear_after()  # Clear locations and events after the test case

        self.assertEqual(_count_location_docs(), 0, "locations collection should be cleared")
        self.assertEqual(_count_event_docs(), 0, "events collection should be cleared")
