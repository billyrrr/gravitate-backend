import unittest

import gravitate.domain.group.pairing
import test.store.model
from gravitate import context
from math import inf

from gravitate.domain.location import Location
from gravitate.domain.rides import RideRequest
from gravitate import distance_func

db = context.Context.db

# rideRequestIds = ["7XO1sUmNMzvlTmSpoyflqJwVCjXQJNOU", "5BWnDYuWgqedQi8ULrtD8yH2VOxI4n2k"]


# def dist_func(p_1, p_2):
#     """
#     Skeleton for distance function
#     :param p_1:
#     :param p_2:
#     :return:
#     """
#     pass

dist_func = distance_func.distance_func

class TestDistanceFunctions(unittest.TestCase):

    def test_latlng_inf_dist(self):
        """
        https://www.movable-type.co.uk/scripts/latlong.html
        :return:
        """
        p_1 = [
            0,
            1,
            50.0359,
            -5.4253
        ]
        p_2 = [
            0,  # Earliest Time
            1,  # Latest Time
            58.3838,  # Latitude
            -3.0412  # Longitude
        ]
        # Distance is 968.9 km > 500 km (Note that this is km)
        dist = dist_func(p_1, p_2)
        self.assertEqual(dist, inf)

    def test_latlng_finite_dist(self):
        p_1 = [
            0,
            1,
            50.0359,
            -5.4253
        ]
        p_2 = [
            0,  # Earliest Time
            1,  # Latest Time
            54.2144,  # Latitude
            -4.3150  # Longitude
        ]
        dist = dist_func(p_1, p_2)
        self.assertLess(dist, inf, "distance should be finite, since"
                                   "p_1 to p_2 have a distance 484.45km < 500km")


class TestExportTuplePoints(unittest.TestCase):

    def setUp(self):
        self.arr = [[12000000, 12005000, 32.8802438, -117.2426505, 'A'],
                    [12000000, 12005000, 32.8796722, -117.2414153, 'B'],
                    [12000000, 12005000, 32.8687404, -117.2306258, 'C'],
                    [12005000, 12006000, 32.8805864, -117.2318744, 'D'],
                    [12007000, 12009000, 32.83228020000001, -117.1480747, 'E'],
                    [12009001, 12009900, 32.8255484, -117.1543703, 'F'],
                    [11000000, 11009000, 32.8248571, -117.1559327, 'G']]

        arr = self.arr

        rideRequests = list()

        configs = list()
        configs_other = [[12000000, 12005000, 'A'],
                    [12000000, 12005000, 'B'],
                    [12000000, 12005000, 'C'],
                    [12005000, 12006000, 'D'],
                    [12007000, 12009000, 'E'],
                    [12009001, 12009900, 'F'],
                    [11000000, 11009000, 'G']]

        addresses = [

            # These are ucsd addresed
            "9500 Gilman Dr, La Jolla, CA 92093",
            "Muir Ln, San Diego, CA 92161",
            "8825 Villa La Jolla Dr, La Jolla, CA 92037",  # Whole foods
            "3390 Voigt Dr, San Diego, CA 92121",  # Canyonview Aquatic Center

            # These are Kearny Mesa Addressed
            "8199 Clairemont Mesa Blvd Suite H, San Diego, CA 92111",  # Camellia
            "4681 Convoy St, San Diego, CA 92111",  # Tajima Japanese Restaurant
            "4646 Convoy St, San Diego, CA 92111"  # Tasty Noodle House

        ]

        locations_ds = [
        {'locationCategory': 'user', 'coordinates': {'latitude': 32.8802438, 'longitude': -117.2426505},
         'address': '9500 Gilman Dr, La Jolla, CA 92093'},
        {'locationCategory': 'user', 'coordinates': {'latitude': 32.8796722, 'longitude': -117.2414153},
         'address': 'Muir Ln, San Diego, CA 92161'},
        {'locationCategory': 'user', 'coordinates': {'latitude': 32.8687404, 'longitude': -117.2306258},
         'address': '8825 Villa La Jolla Dr, La Jolla, CA 92037'},
        {'locationCategory': 'user', 'coordinates': {'latitude': 32.8805864, 'longitude': -117.2318744},
         'address': '3390 Voigt Dr, San Diego, CA 92121'},
        {'locationCategory': 'user', 'coordinates': {'latitude': 32.83228020000001, 'longitude': -117.1480747},
         'address': '8199 Clairemont Mesa Blvd Suite H, San Diego, CA 92111'},
        {'locationCategory': 'user', 'coordinates': {'latitude': 32.8255484, 'longitude': -117.1543703},
         'address': '4681 Convoy St, San Diego, CA 92111'},
        {'locationCategory': 'user', 'coordinates': {'latitude': 32.8248571, 'longitude': -117.1559327},
         'address': '4646 Convoy St, San Diego, CA 92111'},
        ]

        for i in range(len(configs_other)):
            earliest, latest, firestoreRef = configs_other[i]
            address = addresses[i]
            location_d = locations_ds[i]
            ride_request = test.store.model.getMockRideRequest(
                earliest=earliest, latest=latest, firestoreRef=firestoreRef, returnDict=False)

            # Generate Test Locations
            location = Location.from_dict(location_d)
            location.save()
            ref = location.doc_ref
            ride_request.origin_ref = ref

            rideRequests.append(ride_request)

        self.ride_requests = rideRequests

    # def testConstructTupleList(self):
    #     rideRequests: list = self.ride_requests
    #     tuple_list = gravitate.domain.group.pairing._construct_tuple_list(rideRequests)
    #     # Note that this test may fail when the list in a different order.
    #     # The list is allowed to be in a different order.
    #     self.assertListEqual(self.arr, tuple_list)

    def test_construct_tuple_list_new(self):
        rideRequests: list = self.ride_requests
        tuple_list = gravitate.domain.group.pairing._construct_tuple_list_new(rideRequests)
        # Note that this test may fail when the list in a different order.
        # The list is allowed to be in a different order.
        self.assertListEqual(self.arr, tuple_list)

class TestGroupUsers(unittest.TestCase):

    def setUp(self):
        self.arr = [[12000000, 12005000, 'A'],
                    [12000000, 12005000, 'B'],
                    [12000000, 12005000, 'C'],
                    [12005000, 12006000, 'D'],
                    [12007000, 12009000, 'E'],
                    [12009001, 12009900, 'F'],
                    [11000000, 11009000, 'G']]

        arr = self.arr

        rideRequests = list()

        for earliest, latest, firestoreRef in arr:
            rideRequest = test.store.model.getMockRideRequest(
                earliest=earliest, latest=latest, firestoreRef=firestoreRef)
            rideRequests.append(rideRequest)

        self.rideRequests = rideRequests

    def testPairAlgorithm(self):
        arr = self.arr

        paired, unpaired = gravitate.domain.group.pairing._pair(arr=arr)
        expectedPaired = [['A', 'B'], ['C', 'D']]
        expectedUnpaired = [['G'], ['E'], ['F']]

        self.assertListEqual(expectedPaired, paired, 'paired does not match')
        self.assertListEqual(expectedUnpaired, unpaired,
                             'unpaired does not match')

    def testConstructTupleList(self):
        rideRequests: list = self.rideRequests
        tupleList = gravitate.domain.group.pairing._construct_tuple_list(rideRequests)
        # Note that this test may fail when the list in a different order.
        # The list is allowed to be in a different order.
        self.assertListEqual(self.arr, tupleList)

    def testGrouping(self):
        expectedPaired = [['A', 'B'], ['C', 'D']]
        expectedUnpaired = [['G'], ['E'], ['F']]

        rideRequests: list = self.rideRequests
        paired, unpaired = gravitate.domain.group.pairing.pair_ride_requests(rideRequests)

        self.assertListEqual(expectedPaired, paired, 'paired does not match')
        self.assertListEqual(expectedUnpaired, unpaired,
                             'unpaired does not match')
