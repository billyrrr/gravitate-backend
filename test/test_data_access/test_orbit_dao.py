import unittest
from unittest.mock import Mock

from gravitate import data_access
from gravitate.models import Orbit
from gravitate import context
from test.store import orbitDict


class OrbitDaoTest(unittest.TestCase):

    def setUp(self):
        self.db = context.Context.db
        self.to_delete = list()

    def testCreateOrbit(self):
        newOrbit = Orbit.from_dict(orbitDict)
        orbitRef = data_access.OrbitDao().create(newOrbit)
        self.to_delete.append(orbitRef)
        self.assertIsNotNone(orbitRef)

    def tearDown(self):
        for ref in self.to_delete:
            ref.delete()

    def testMockCreateOrbit(self):
        m = Mock()
        newOrbit = Orbit.from_dict(orbitDict)
        orbitRef = m(newOrbit)
        print(m.call_args_list)
