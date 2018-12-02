from controllers.group_user import pair
from controllers.grouping import constructTupleList, pairRideRequests, constructGroups, groupRideRequests
from data_access.ride_request_dao import RideRequestGenericDao
from controllers import groupingutils
from models.ride_request import RideRequest
from models.orbit import Orbit
import factory
import unittest
import config
from google.cloud import firestore

db = config.Context.db


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

        pair(arr=arr, paired=paired, unpaired=unpaired)
        expectedPaired = [['A', 'B'], ['C', 'D']]
        expectedUnpaired = [['G'], ['E'], ['F']]

        self.assertListEqual(expectedPaired, paired, 'paired does not match')
        self.assertListEqual(expectedUnpaired, unpaired,
                             'unpaired does not match')

    def testConstructTupleList(self):
        rideRequests: list = self.rideRequests
        tupleList = constructTupleList(rideRequests)
        # Note that this test may fail when the list in a different order.
        # The list is allowed to be in a different order.
        self.assertListEqual(self.arr, tupleList)

    def testGrouping(self):
        expectedPaired = [['A', 'B'], ['C', 'D']]
        expectedUnpaired = [['G'], ['E'], ['F']]

        rideRequests: list = self.rideRequests
        paired, unpaired = pairRideRequests(rideRequests)

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
                earliest=earliest, latest=latest, firestoreRef=firestoreRef)
            transaction = db.transaction()
            RideRequestGenericDao().setRideRequestWithTransaction(
                transaction, rideRequest, firestoreRef)
            rideRequest.setFirestoreRef(firestoreRef)
            rideRequests.append(rideRequest)

        self.rideRequests = rideRequests

    def testConstructTupleList(self):
        rideRequests: list = self.rideRequests
        tupleList = constructTupleList(rideRequests)
        # Note that this test may fail when the list in a different order.
        # The list is allowed to be in a different order.
        self.assertListEqual(self.arr, tupleList)

    def testConstructGroup(self):
        paired = [[RideRequestGenericDao().rideRequestCollectionRef.document('A'),  RideRequestGenericDao().rideRequestCollectionRef.document('B')],
                  [RideRequestGenericDao().rideRequestCollectionRef.document('C'),  RideRequestGenericDao().rideRequestCollectionRef.document('D')]]
        groups = list()
        constructGroups(groups, paired)

    def testGrouping(self):
        expectedPaired = [[RideRequestGenericDao().rideRequestCollectionRef.document('A'),  RideRequestGenericDao().rideRequestCollectionRef.document('B')],
                          [RideRequestGenericDao().rideRequestCollectionRef.document('C'),  RideRequestGenericDao().rideRequestCollectionRef.document('D')]]
        expectedUnpaired = [[RideRequestGenericDao().rideRequestCollectionRef.document('G')], [RideRequestGenericDao(
        ).rideRequestCollectionRef.document('E')], [RideRequestGenericDao().rideRequestCollectionRef.document('F')]]

        rideRequests: list = self.rideRequests
        paired, unpaired = pairRideRequests(rideRequests)

        self.assertListEqual(expectedPaired, paired, 'paired does not match')
        self.assertListEqual(expectedUnpaired, unpaired,
                             'unpaired does not match')

    def testPrimaryGroupingFunc(self):
        groupRideRequests(self.rideRequests)

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

        rideRequestDict = {

            'rideCategory': 'airportRide',
            'pickupAddress': "Tenaya Hall, San Diego, CA 92161",
            'driverStatus': False,
            'orbitRef': None,
            'target': {'eventCategory': 'airportRide',
                       'toEvent': True,
                       'arriveAtEventTime':
                       {'earliest': 1545058800, 'latest': 1545069600}},
            'eventRef': db.document('events', 'testeventid1'),
            'userId': 'SQytDq13q00e0N3H4agR',
            'hasCheckedIn': False,
            'pricing': 987654321,
            "baggages": dict(),
            "disabilities": dict(),
            'flightLocalTime': "2018-12-17T12:00:00.000",
            'flightNumber': "DL89",
            "airportLocation": db.document("locations", "testairportlocationid1")

        }

        rideRequest = RideRequest.fromDict(rideRequestDict)
        rideRequest.setFirestoreRef(db.document(
            'rideRequests', 'testriderequestid1'))

        groupingutils.placeInOrbit(rideRequest, orbit)
        userTicketPairsDict = orbit.toDict()["userTicketPairs"]
        expectedDict = {
            'SQytDq13q00e0N3H4agR' : {
                "rideRequestRef": db.document('rideRequests', 'testriderequestid1'),
                "userWillDrive": False,
                "hasCheckedIn": False,
                "inChat": False,
                "pickupAddress": "Tenaya Hall, San Diego, CA 92161"
            }
        }
        self.assertDictEqual(userTicketPairsDict, expectedDict)
