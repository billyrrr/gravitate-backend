import unittest
from tests import factory 
from controllers import eventscheduleutils
from data_access import EventScheduleGenericDao
from models import EventSchedule

eventScheduleDict = {
	"destName": "LAX",
	"destTime": None,
    "flightTime": "2018-12-17T12:00:00.000",
    "memberProfilePhotoUrls": [],
    "pickupAddress": "Tenaya Hall, San Diego, CA 92161",
    "pending": True,
	"rideRequestRef": "/rideRequests/testRef1",
    "locationRef": "/locations/AedTfnR2FhaLnVHriAMn",
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

    def testCreateCompletedRideRequest(self):
        raise NotImplementedError
        # rideRequest: make a mock ride request that is matched to an orbit
        # orbit: make an orbit that is matched to a pair of users

# class EventScheduleDAOTest(unittest.TestCase):

    