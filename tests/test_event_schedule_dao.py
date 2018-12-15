import unittest
from tests import factory 
from controllers import eventscheduleutils
from data_access import EventScheduleGenericDao
from models import EventSchedule
from controllers.eventscheduleutils import getMemberProfilePhotoUrls
from google.cloud.firestore import Transaction, DocumentReference, DocumentSnapshot, CollectionReference, Client, transactional
from models.orbit import Orbit
from tests import config

CTX = config.Context
auth = config.auth

db = CTX.db

eventScheduleDict = {
	"destName": "LAX",
	"destTime": None,
    "flightTime": "2018-12-17T12:00:00.000",
    "memberProfilePhotoUrls": [],
    "pickupAddress": "Tenaya Hall, San Diego, CA 92161",
    "pending": True,
	"rideRequestRef": "/rideRequests/testA",
    "locationRef": "/locations/Bdn07rFaesdlg8whfjpV",
	"orbitRef": None
}

class EventScheduleTest(unittest.TestCase):
    
    def testFromAndToDict(self):
        eventSchedule = EventSchedule.fromDict(eventScheduleDict)
        self.assertDictEqual(eventScheduleDict, eventSchedule.toDict())

    def testCreate(self):
        rideRequest = factory.getMockRideRequest()
        eventSch = eventscheduleutils.buildEventSchedule(rideRequest)
        self.assertEquals(eventScheduleDict, eventSch.toDict())

    def testPopulateProfileUrls(self):
        orbitRef: DocumentReference = db.collection(u'orbits').document("WQiIEsGlVbU8a8F1la45")
        snapshot: DocumentSnapshot = orbitRef.get()
        if snapshot.exists:
            orbit: Orbit = Orbit.fromDict(snapshot.to_dict())
            print(getMemberProfilePhotoUrls(orbit))
        else:
            print("Not Found")
            return False

    def testCreateCompletedRideRequest(self):
        raise NotImplementedError
        # rideRequest: make a mock ride request that is matched to an orbit
        # orbit: make an orbit that is matched to a pair of users

# class EventScheduleDAOTest(unittest.TestCase):

    