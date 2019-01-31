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

        rideRequests = list()

        for earliest, latest, firestoreRef in arr:
            rideRequest = test.store.model.getMockRideRequest(
                earliest=earliest, latest=latest, firestoreRef=firestoreRef)
            rideRequests.append(rideRequest)

        self.rideRequests = rideRequests

    def testPairAlgorithm(self):
        arr = self.arr

        # paired = []
        # unpaired = []

        paired, unpaired = gravitate.controllers.grouping.pairing.pair(arr=arr)
        expectedPaired = [['A', 'B'], ['C', 'D']]
        expectedUnpaired = [['G'], ['E'], ['F']]

        self.assertListEqual(expectedPaired, paired, 'paired does not match')
        self.assertListEqual(expectedUnpaired, unpaired,
                             'unpaired does not match')

    def testConstructTupleList(self):
        rideRequests: list = self.rideRequests
        tupleList = gravitate.controllers.grouping.pairing.construct_tuple_list(rideRequests)
        # Note that this test may fail when the list in a different order.
        # The list is allowed to be in a different order.
        self.assertListEqual(self.arr, tupleList)

    def testGrouping(self):
        expectedPaired = [['A', 'B'], ['C', 'D']]
        expectedUnpaired = [['G'], ['E'], ['F']]

        rideRequests: list = self.rideRequests
        paired, unpaired = gravitate.controllers.grouping.pairing.pair_ride_requests(rideRequests)

        self.assertListEqual(expectedPaired, paired, 'paired does not match')
        self.assertListEqual(expectedUnpaired, unpaired,
                             'unpaired does not match')
