import unittest

from gravitate import config, data_access as data_access
from gravitate.models import Orbit
from test.models.test_orbit import orbitDict


class OrbitDaoTest(unittest.TestCase):
    def setUp(self):
        self.db = config.Context.db

    def testCreateOrbit(self):
        newOrbit = Orbit.fromDict(orbitDict)
        orbitRef = data_access.OrbitDao().create(newOrbit)
        self.assertIsNotNone(orbitRef)