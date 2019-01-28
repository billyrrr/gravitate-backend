import unittest
from gravitate.models import Orbit
from test.store import orbitDict


class OrbitTest(unittest.TestCase):

    def testInitWithDict(self):
        newOrbit = Orbit.from_dict(orbitDict)
        dictNewOrbit = newOrbit.to_dict()
        self.assertDictEqual(orbitDict, dictNewOrbit)
