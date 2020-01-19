import unittest

import gravitate.domain.group.pairing
import test.store.model
from gravitate.domain.rides import RideRequestGenericDao
from gravitate.domain.group.utils import _add_to_orbit
from gravitate.domain.orbit.models import Orbit
from gravitate.domain.rides import RideRequest
from gravitate import context
from test import scripts

db = context.Context.db

rideRequestIds = ["7XO1sUmNMzvlTmSpoyflqJwVCjXQJNOU", "5BWnDYuWgqedQi8ULrtD8yH2VOxI4n2k"]

#
# class TestTempForceGroupUsers(unittest.TestCase):
#
#     def testMatchTwo(self):
#         result = actions.group_two(rideRequestIds)
#         print(result)
#         self.assertIsNone(result)  # So that we see debug log
#def testRemoveMatch(self):
#         # rideRequestId = "nOb3TWzUpSopqhNbwVxyfnTU7u91pRmO" # "gganvzHRUCyGiLf2tZAle5Z11HicZ6dR" # "PBQILbyLowYlv2WZsDRnPvP61lM6NzoC" # "9msl3amhAj503pAtSjSQod4qy6N26e7h" # "5BWnDYuWgqedQi8ULrtD8yH2VOxI4n2k" # "7XO1sUmNMzvlTmSpoyflqJwVCjXQJNOU"
#         rideRequestId = "ZjOsvcOHyUKKAJwYnCSHNM0cC8YsEjWo"
#         rideRequestRef = RideRequestGenericDao().rideRequestCollectionRef.document(rideRequestId)
#         rideRequest = RideRequestGenericDao().get(rideRequestRef)
#         orbitRef = rideRequest.orbit_ref
#         orbit = OrbitDao().get(orbitRef)
#         remove_from_orbit(rideRequest, orbit)
#


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


class TestGroupUsersWithRideRequestRef(unittest.TestCase):

    def tearDown(self):
        self.c.clear_after()
        for earliest, latest, firestoreRef in self.arr:
            RideRequestGenericDao().delete(firestoreRef)

    def setUp(self):
        self.c = scripts.SetUpTestDatabase()
        self.c.clear_before()
        self.c.generate_test_data(start_string="2018-12-17T08:00:00.000", num_days=5)
        self.maxDiff = None
        self.arr = [[12000000, 12005000, RideRequestGenericDao().rideRequestCollectionRef.document('A')],
                    [12000000, 12005000, RideRequestGenericDao(
                    ).rideRequestCollectionRef.document('B')],
                    [12000000, 12005000, RideRequestGenericDao(
                    ).rideRequestCollectionRef.document('C')],
                    [12005000, 12006000, RideRequestGenericDao(
                    ).rideRequestCollectionRef.document('D')],
                    [12007000, 12009000, RideRequestGenericDao(
                    ).rideRequestCollectionRef.document('E')],
                    [12009001, 12009900, RideRequestGenericDao(
                    ).rideRequestCollectionRef.document('F')],
                    [11000000, 11009000, RideRequestGenericDao().rideRequestCollectionRef.document('G')]]

        arr = self.arr

        rideRequests = list()

        for earliest, latest, firestoreRef in arr:
            rideRequest = test.store.model.getMockRideRequest(
                earliest=earliest, latest=latest, firestoreRef=firestoreRef,
                userId='userIdA' if firestoreRef.id == 'A' else 'userIdBmore')
            transaction = db.transaction()
            RideRequestGenericDao().set_with_transaction(
                transaction, rideRequest, firestoreRef)
            rideRequest.set_firestore_ref(firestoreRef)
            rideRequests.append(rideRequest)

        self.rideRequests = rideRequests


    def testConstructTupleList(self):
        rideRequests: list = self.rideRequests
        tupleList = gravitate.domain.group.pairing._construct_tuple_list(rideRequests)
        # Note that this test may fail when the list in a different order.
        # The list is allowed to be in a different order.
        self.assertListEqual(self.arr, tupleList)

    def testGrouping(self):
        expectedPaired = [[RideRequestGenericDao().rideRequestCollectionRef.document('A'),
                           RideRequestGenericDao().rideRequestCollectionRef.document('B')],
                          [RideRequestGenericDao().rideRequestCollectionRef.document('C'),
                           RideRequestGenericDao().rideRequestCollectionRef.document('D')]]
        expectedUnpaired = [[RideRequestGenericDao().rideRequestCollectionRef.document('G')], [RideRequestGenericDao(
        ).rideRequestCollectionRef.document('E')], [RideRequestGenericDao().rideRequestCollectionRef.document('F')]]

        rideRequests: list = self.rideRequests
        paired, unpaired = gravitate.domain.group.pairing.pair_ride_requests(rideRequests)

        self.assertListEqual(expectedPaired, paired, 'paired does not match')
        self.assertListEqual(expectedUnpaired, unpaired,
                             'unpaired does not match')

    def testPlaceInOrbit(self):
        orbitDict = {
            "orbitCategory": "airportRide",
            "eventRef": "testeventref1",
            "userTicketPairs": {
            },
            "chatroomRef": "testchatroomref1",
            "costEstimate": 987654321,
            "status": 1
        }

        orbit = Orbit.from_dict(orbitDict)

        rideRequestDict = test.store.model.getMockRideRequest(
            useDocumentRef=True, returnDict=True, returnSubset=False)

        rideRequest = RideRequest.from_dict(rideRequestDict)
        rideRequest.set_firestore_ref(db.document(
            'rideRequests', 'testriderequestid1'))

        _add_to_orbit(rideRequest, orbit)
        userTicketPairsDict = orbit.to_dict()["userTicketPairs"]
        expectedDict = {
            rideRequest.user_id: {
                "rideRequestRef": db.document('rideRequests', 'testriderequestid1'),
                "userWillDrive": False,
                "hasCheckedIn": False,
                "inChat": False,
                "pickupAddress": "Tenaya Hall, San Diego, CA 92161"
            }
        }
        self.assertDictEqual(userTicketPairsDict, expectedDict)
