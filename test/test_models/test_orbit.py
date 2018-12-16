import unittest
from gravitate.models import Orbit
from test.factory import orbitDict


class OrbitTest(unittest.TestCase):

    def testInitWithDict(self):
        newOrbit = Orbit.fromDict(orbitDict)
        dictNewOrbit = newOrbit.toDict()
        self.assertDictEqual(orbitDict, dictNewOrbit)
