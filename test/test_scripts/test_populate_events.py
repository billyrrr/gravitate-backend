import unittest
from gravitate.scripts import populate_airport_events, populate_locations


class PopulateEventCommandTest(unittest.TestCase):

    def setUp(self):
        self.refs_to_delete = list()
        c = populate_locations.PopulateLocationCommand()
        refs = c.execute()
        self.refs_to_delete.append(refs.pop())
        assert len(refs) == 0

    def test_generate_events(self):
        c = populate_airport_events.PopulateEventCommand(start_string="2018-12-01T08:00:00.000", num_days=5)
        refs = c.execute()
        self.refs_to_delete = refs
        self.assertEqual(5, len(refs), "number of DocumentReference should be 5")

    def tearDown(self):
        for ref in self.refs_to_delete:
            ref.delete()
