import unittest
from gravitate.data_access import LocationGenericDao


class LocationDAOTest(unittest.TestCase):

    # def setUp(self):
    #     self.user = User.fromDict(userDict)

    def testFindByAirportCode(self):
        result = LocationGenericDao().findByAirportCode('LAX')
        self.assertNotEqual(None, result, 'Should return a result. ')
