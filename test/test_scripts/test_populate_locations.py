import unittest
from gravitate.scripts import populate_locations


class PopulateLocationCommandTest(unittest.TestCase):

    def setUp(self):
        self.refs_to_delete = list()

    def test_generate_locations(self):
        c = populate_locations.PopulateLocationCommand()
        refs = c.execute()
        self.refs_to_delete = refs
        self.assertEqual(len(refs), 1, "number of DocumentReference should be 1")

    def tearDown(self):
        for ref in self.refs_to_delete:
            ref.delete()
