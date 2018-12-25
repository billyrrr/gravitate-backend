import unittest
from unittest.mock import Mock

from gravitate import data_access
from test import context
from gravitate.models import Orbit
from test.factory import orbitDict


class OrbitDaoTest(unittest.TestCase):

    def setUp(self):
        self.db = context.Context.db

    def testCreateOrbit(self):
        newOrbit = Orbit.from_dict(orbitDict)
        orbitRef = data_access.OrbitDao().create(newOrbit)
        self.assertIsNotNone(orbitRef)

    def testMockCreateOrbit(self):
        m = Mock()
        newOrbit = Orbit.from_dict(orbitDict)
        orbitRef = m(newOrbit)
        print(m.call_args_list)
