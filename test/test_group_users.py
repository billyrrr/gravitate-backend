from gravitate.controllers import grouping
from gravitate.controllers.groupingutils import placeInOrbit
from gravitate.data_access.ride_request_dao import RideRequestGenericDao
from gravitate.models.ride_request import RideRequest
from gravitate.models.orbit import Orbit
from test import factory
import unittest
from test import config

db = config.Context.db

rideRequestIds = ["7XO1sUmNMzvlTmSpoyflqJwVCjXQJNOU", "5BWnDYuWgqedQi8ULrtD8yH2VOxI4n2k"]


class TestTempForceGroupUsers(unittest.TestCase):

    def testMatchTwo(self):
        result = grouping.forceMatchTwoRideRequests(rideRequestIds)
        print(result)
        self.assertIsNone(result)  # So that we see debug log

    def testRemoveMatch(self):
        # rideRequestId = "nOb3TWzUpSopqhNbwVxyfnTU7u91pRmO" # "gganvzHRUCyGiLf2tZAle5Z11HicZ6dR" # "PBQILbyLowYlv2WZsDRnPvP61lM6NzoC" # "9msl3amhAj503pAtSjSQod4qy6N26e7h" # "5BWnDYuWgqedQi8ULrtD8yH2VOxI4n2k" # "7XO1sUmNMzvlTmSpoyflqJwVCjXQJNOU"
        rideRequestId = "pQhkYYht8fzLe612yMh7U7XlcE5zT3vg"
        rideRequestRef = RideRequestGenericDao().rideRequestCollectionRef.document(rideRequestId)
        grouping.remove(rideRequestRef)


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
            rideRequest = factory.getMockRideRequest(
                earliest=earliest, latest=latest, firestoreRef=firestoreRef)
            rideRequests.append(rideRequest)

        self.rideRequests = rideRequests

    def testPairAlgorithm(self):
        arr = self.arr

        paired = []
        unpaired = []

        grouping.pair(arr=arr, paired=paired, unpaired=unpaired)
        expectedPaired = [['A', 'B'], ['C', 'D']]
        expectedUnpaired = [['G'], ['E'], ['F']]

        self.assertListEqual(expectedPaired, paired, 'paired does not match')
        self.assertListEqual(expectedUnpaired, unpaired,
                             'unpaired does not match')

    def testConstructTupleList(self):
        rideRequests: list = self.rideRequests
        tupleList = grouping.constructTupleList(rideRequests)
        # Note that this test may fail when the list in a different order.
        # The list is allowed to be in a different order.
        self.assertListEqual(self.arr, tupleList)

    def testGrouping(self):
        expectedPaired = [['A', 'B'], ['C', 'D']]
        expectedUnpaired = [['G'], ['E'], ['F']]

        rideRequests: list = self.rideRequests
        paired, unpaired = grouping.pairRideRequests(rideRequests)

        self.assertListEqual(expectedPaired, paired, 'paired does not match')
        self.assertListEqual(expectedUnpaired, unpaired,
                             'unpaired does not match')


class TestGroupUsersWithRideRequestRef(unittest.TestCase):

    def setUp(self):
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
            rideRequest = factory.getMockRideRequest(
                earliest=earliest, latest=latest, firestoreRef=firestoreRef,
                userId='userIdA' if firestoreRef.id == 'A' else 'userIdBmore')
            transaction = db.transaction()
            RideRequestGenericDao().setWithTransaction(
                transaction, rideRequest, firestoreRef)
            rideRequest.setFirestoreRef(firestoreRef)
            rideRequests.append(rideRequest)

        self.rideRequests = rideRequests

    def testConstructTupleList(self):
        rideRequests: list = self.rideRequests
        tupleList = grouping.constructTupleList(rideRequests)
        # Note that this test may fail when the list in a different order.
        # The list is allowed to be in a different order.
        self.assertListEqual(self.arr, tupleList)

    def testConstructGroup(self):
        paired = [[RideRequestGenericDao().rideRequestCollectionRef.document('A'),
                   RideRequestGenericDao().rideRequestCollectionRef.document('B')],
                  [RideRequestGenericDao().rideRequestCollectionRef.document('C'),
                   RideRequestGenericDao().rideRequestCollectionRef.document('D')]]
        groups = list()
        grouping.constructGroups(groups, paired)

    def testGrouping(self):
        expectedPaired = [[RideRequestGenericDao().rideRequestCollectionRef.document('A'),
                           RideRequestGenericDao().rideRequestCollectionRef.document('B')],
                          [RideRequestGenericDao().rideRequestCollectionRef.document('C'),
                           RideRequestGenericDao().rideRequestCollectionRef.document('D')]]
        expectedUnpaired = [[RideRequestGenericDao().rideRequestCollectionRef.document('G')], [RideRequestGenericDao(
        ).rideRequestCollectionRef.document('E')], [RideRequestGenericDao().rideRequestCollectionRef.document('F')]]

        rideRequests: list = self.rideRequests
        paired, unpaired = grouping.pairRideRequests(rideRequests)

        self.assertListEqual(expectedPaired, paired, 'paired does not match')
        self.assertListEqual(expectedUnpaired, unpaired,
                             'unpaired does not match')

    def testPrimaryGroupingFunc(self):
        grouping.groupRideRequests(self.rideRequests)

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

        orbit = Orbit.fromDict(orbitDict)

        rideRequestDict = factory.getMockRideRequest(
            useDocumentRef=True, returnDict=True, returnSubset=False)

        rideRequest = RideRequest.fromDict(rideRequestDict)
        rideRequest.setFirestoreRef(db.document(
            'rideRequests', 'testriderequestid1'))

        placeInOrbit(rideRequest, orbit)
        userTicketPairsDict = orbit.toDict()["userTicketPairs"]
        expectedDict = {
            'SQytDq13q00e0N3H4agR': {
                "rideRequestRef": db.document('rideRequests', 'testriderequestid1'),
                "userWillDrive": False,
                "hasCheckedIn": False,
                "inChat": False,
                "pickupAddress": "Tenaya Hall, San Diego, CA 92161"
            }
        }
        self.assertDictEqual(userTicketPairsDict, expectedDict)
