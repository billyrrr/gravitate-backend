import unittest
<<<<<<< HEAD
from data_access import EventScheduleGenericDao
from google.cloud.firestore import DocumentReference
=======
from tests import factory 
from controllers import eventscheduleutils
from data_access import EventScheduleGenericDao

>>>>>>> origin/master

eventScheduleDict = {
	"destName": None,
	"destTime": None,
    "flightTime": "2018-12-17T12:00:00.000",
    "memberProfilePhotoUrls": [],
    "pickupAddress": "Tenaya Hall, San Diego, CA 92161",
    "pending": None,
	"rideRequestRef": "/rideRequests/testRef1",
	"orbitRef": None
}

class EventScheduleDAOTest(unittest.TestCase):


    def testCreate(self):
<<<<<<< HEAD
        eventScheduleRef: DocumentReference = EventScheduleGenericDao().create(self.eventScheduleRef)
        self.eventScheduleRef.setFirestoreRef(eventScheduleRef)
        print("eventScheduleRef = {}".format(eventScheduleRef))
=======
        rideRequest = factory.getMockRideRequest()
        eventSch = eventscheduleutils.buildEventSchedule(rideRequest)
        self.assertEquals(eventScheduleDict, eventSch.toDict())
>>>>>>> origin/master
