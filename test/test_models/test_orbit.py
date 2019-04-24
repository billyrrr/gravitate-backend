import unittest

from gravitate.domain.orbit import Orbit
from test.store import orbitDict


class OrbitTest(unittest.TestCase):

    def test_init_with_dict(self):
        new_orbit = Orbit.from_dict(orbitDict)
        dict_new_orbit = new_orbit.to_dict()
        self.assertDictEqual(orbitDict, dict_new_orbit)
