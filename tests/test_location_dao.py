import unittest
from data_access.location_dao import LocationGenericDao


class LocationDAOTest(unittest.TestCase):

    # def setUp(self):
    #     self.user = User.fromDict(userDict)

    def testFindByAirportCode(self):
        result = LocationGenericDao().findByAirportCode('LAX')
        self.assertNotEqual(None, result, 'Should return a result. ')
