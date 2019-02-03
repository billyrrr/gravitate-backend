import gravitate.domain.grouping.pairing
# import gravitate.controllers.grouping.remove
import test.store.model
from gravitate.domain.grouping import grouping
import gravitate.domain.grouping.utils as grouping_utils
from gravitate.domain.grouping.utils import _add_to_orbit
from gravitate.data_access import OrbitDao
from gravitate.data_access.ride_request_dao import RideRequestGenericDao
from gravitate.models.ride_request import RideRequest
from gravitate.models.orbit import Orbit
import unittest
from test import context

db = context.Context.db

rideRequestIds = ["7XO1sUmNMzvlTmSpoyflqJwVCjXQJNOU", "5BWnDYuWgqedQi8ULrtD8yH2VOxI4n2k"]


class TestOrbitGroupHelpers(unittest.TestCase):

    def setUp(self):
        self.r = RideRequestGenericDao().get_by_id("CmTvs1VcnavAnanhl8Nu00OmWkJYou2o")
        self.o = OrbitDao().get_by_id("1mozA22dmuFWBZbLRkdg")

    def test_add(self):

        is_successful = grouping_utils.add_orbit_to_ride_request(self.r, self.o)
        self.assertTrue(is_successful)

    def test_validate_add(self):
        is_valid = grouping_utils._validate_to_add(self.r, self.o)
        self.assertTrue(is_valid)

#
# class TestTempForceGroupUsers(unittest.TestCase):
#
#     def testMatchTwo(self):
#         result = grouping.group_two(rideRequestIds)
#         print(result)
#         self.assertIsNone(result)  # So that we see debug log
#
#     def testRemoveMatch(self):
#         # rideRequestId = "nOb3TWzUpSopqhNbwVxyfnTU7u91pRmO" # "gganvzHRUCyGiLf2tZAle5Z11HicZ6dR" # "PBQILbyLowYlv2WZsDRnPvP61lM6NzoC" # "9msl3amhAj503pAtSjSQod4qy6N26e7h" # "5BWnDYuWgqedQi8ULrtD8yH2VOxI4n2k" # "7XO1sUmNMzvlTmSpoyflqJwVCjXQJNOU"
#         rideRequestId = "ZjOsvcOHyUKKAJwYnCSHNM0cC8YsEjWo"
#         rideRequestRef = RideRequestGenericDao().rideRequestCollectionRef.document(rideRequestId)
#         gravitate.controllers.grouping.remove.remove(rideRequestRef)


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
        tupleList = gravitate.domain.grouping.pairing.construct_tuple_list(rideRequests)
        # Note that this test may fail when the list in a different order.
        # The list is allowed to be in a different order.
        self.assertListEqual(self.arr, tupleList)

    def testConstructGroup(self):
        paired = [[RideRequestGenericDao().rideRequestCollectionRef.document('A'),
                   RideRequestGenericDao().rideRequestCollectionRef.document('B')],
                  [RideRequestGenericDao().rideRequestCollectionRef.document('C'),
                   RideRequestGenericDao().rideRequestCollectionRef.document('D')]]
        groups = grouping.construct_groups(paired)

    def testGrouping(self):
        expectedPaired = [[RideRequestGenericDao().rideRequestCollectionRef.document('A'),
                           RideRequestGenericDao().rideRequestCollectionRef.document('B')],
                          [RideRequestGenericDao().rideRequestCollectionRef.document('C'),
                           RideRequestGenericDao().rideRequestCollectionRef.document('D')]]
        expectedUnpaired = [[RideRequestGenericDao().rideRequestCollectionRef.document('G')], [RideRequestGenericDao(
        ).rideRequestCollectionRef.document('E')], [RideRequestGenericDao().rideRequestCollectionRef.document('F')]]

        rideRequests: list = self.rideRequests
        paired, unpaired = gravitate.domain.grouping.pairing.pair_ride_requests(rideRequests)

        self.assertListEqual(expectedPaired, paired, 'paired does not match')
        self.assertListEqual(expectedUnpaired, unpaired,
                             'unpaired does not match')

    def testPrimaryGroupingFunc(self):
        grouping.group_ride_requests(self.rideRequests)

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
            'SQytDq13q00e0N3H4agR': {
                "rideRequestRef": db.document('rideRequests', 'testriderequestid1'),
                "userWillDrive": False,
                "hasCheckedIn": False,
                "inChat": False,
                "pickupAddress": "Tenaya Hall, San Diego, CA 92161"
            }
        }
        self.assertDictEqual(userTicketPairsDict, expectedDict)
