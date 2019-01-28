import unittest

import test.store.model
from gravitate.controllers import eventscheduleutils
from gravitate.models import AirportEventSchedule
from test import store

eventScheduleDict = store.eventScheduleDict.copy()

class EventScheduleDaoTest(unittest.TestCase):

    def testFromAndToDict(self):
        eventSchedule = AirportEventSchedule.from_dict(eventScheduleDict)
        self.assertDictEqual(eventScheduleDict, eventSchedule.to_dict())

    def testCreate(self):
        rideRequest = test.store.model.getMockRideRequest()
        location = test.store.model.getLocation()
        eventSch = eventscheduleutils.create_event_schedule(rideRequest, location)
        eventScheduleDict["destTime"] = 1545069600  # .destTime is used off-label for sorting
        self.assertDictEqual(eventScheduleDict, eventSch.to_dict())
