import unittest
from tests import factory 
from controllers import eventscheduleutils
from data_access import EventScheduleGenericDao
from models import EventSchedule

eventScheduleDict = {
	"destName": None,
	"destTime": None,
    "flightTime": "2018-12-17T12:00:00.000",
    "memberProfilePhotoUrls": [],
    "pickupAddress": "Tenaya Hall, San Diego, CA 92161",
    "pending": True,
	"rideRequestRef": "/rideRequests/testRef1",
	"orbitRef": None
}

class EventScheduleTest(unittest.TestCase):
    
    def testFromAndToDict(self):
        eventSchedule = EventSchedule.fromDict(eventScheduleDict)
        self.assertDictEqual(eventScheduleDict, eventSchedule.toDict())

class EventScheduleDAOTest(unittest.TestCase):

    def testCreate(self):
        rideRequest = factory.getMockRideRequest()
        eventSch = eventscheduleutils.buildEventSchedule(rideRequest)
        self.assertEquals(eventScheduleDict, eventSch.toDict())
