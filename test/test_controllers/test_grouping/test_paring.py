import unittest

import gravitate.controllers
import test.store


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

        ride_requests = list()

        for earliest, latest, firestoreRef in arr:
            ride_request = test.store.model.getMockRideRequest(
                earliest=earliest, latest=latest, firestoreRef=firestoreRef)
            ride_requests.append(ride_request)

        self.rideRequests = ride_requests

    def testPairAlgorithm(self):
        arr = self.arr

        # paired = []
        # unpaired = []

        paired, unpaired = gravitate.controllers.grouping.pairing.pair(arr=arr)
        expected_paired = [['A', 'B'], ['C', 'D']]
        expected_unpaired = [['G'], ['E'], ['F']]

        self.assertListEqual(expected_paired, paired, 'paired does not match')
        self.assertListEqual(expected_unpaired, unpaired,
                             'unpaired does not match')

    def testConstructTupleList(self):
        ride_requests: list = self.rideRequests
        tuple_list = gravitate.controllers.grouping.pairing.construct_tuple_list(ride_requests)
        # Note that this test may fail when the list in a different order.
        # The list is allowed to be in a different order.
        self.assertListEqual(self.arr, tuple_list)

    def testGrouping(self):
        expected_paired = [['A', 'B'], ['C', 'D']]
        expected_unpaired = [['G'], ['E'], ['F']]

        ride_requests: list = self.rideRequests
        paired, unpaired = gravitate.controllers.grouping.pairing.pair_ride_requests(ride_requests)

        self.assertListEqual(expected_paired, paired, 'paired does not match')
        self.assertListEqual(expected_unpaired, unpaired,
                             'unpaired does not match')
