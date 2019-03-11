from unittest import TestCase, skip

from google.cloud import firestore

from gravitate.api_server.ride_request.deprecated_utils import fill_ride_request_dict_with_form, \
    fill_ride_request_dict_builder_regression
from gravitate.domain.event.dao import EventDao
from gravitate.domain.request_ride.utils import check_duplicate
from gravitate.domain.rides import RideRequest
from test.store import FormDictFactory
from test.test_main import userId, db


@skip("test is not functional for now, add setup first")
class TestCreateRideRequestLogics(TestCase):
    """
    Note that the module being tested is deprecated. The test is preserved for reference. 

    """

    def setUp(self):
        self.maxDiff = None

    def testHasDuplicateEvent(self):
        userId: str = "44lOjfDJoifnq1IMRdk4VKtPutF3"
        eventId: str = "8GKfUA2AbGCrgRo7n6Rt"
        eventRef: firestore.DocumentReference = EventDao().get_ref(eventId)
        result = check_duplicate(userId, eventRef)
        # Assert that check_duplicate is False since we have an entry
        #   with equal eventRef and userId field in the database
        self.assertNotEqual(result, False)


    # def testSaveRideRequestToDb(self):
    #     mockForm = FormDictFactory().create(hasEarliestLatest=False, returnDict=False)
    #     rideRequestDict, _ = fill_ride_request_dict_with_form(mockForm, userId)
    #     result = RideRequest.from_dict(rideRequestDict)
    #     saveRideRequest(result)

    def testFillRideRequestDict(self):
        mockForm = FormDictFactory().create(hasEarliestLatest=False, returnDict=False)
        result, _ = fill_ride_request_dict_with_form(mockForm, userId)
        valueExpected = RideRequest.from_dict({

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
            "airportLocation": db.document("locations", "testairportlocationid1"),
            "requestCompletion": False

        }).to_dict()
        self.assertDictEqual(valueExpected, result)
        self.assertIsNotNone(result["eventRef"])
        self.assertIsNotNone(result["airportLocation"])

    def testFillRideRequestDictNew(self):
        mockForm = FormDictFactory().create(hasEarliestLatest=False, returnDict=False)
        result, _ = fill_ride_request_dict_builder_regression(mockForm, userId)
        valueExpected = RideRequest.from_dict({

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
            "airportLocation": db.document("locations", "testairportlocationid1"),
            "requestCompletion": False

        }).to_dict()
        self.assertDictEqual(valueExpected, result)
        self.assertIsNotNone(result["eventRef"])
        self.assertIsNotNone(result["airportLocation"])
