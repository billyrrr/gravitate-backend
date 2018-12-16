import unittest

import test.factory.model
from gravitate.controllers import eventscheduleutils
from gravitate.models import EventSchedule
from test import factory
from test.factory import eventScheduleDict


class EventScheduleDaoTest(unittest.TestCase):

    def testFromAndToDict(self):
        eventSchedule = EventSchedule.fromDict(eventScheduleDict)
        self.assertDictEqual(eventScheduleDict, eventSchedule.toDict())

    def testCreate(self):
        rideRequest = test.factory.model.getMockRideRequest()
        location = test.factory.model.getLocation()
        eventSch = eventscheduleutils.buildEventSchedule(rideRequest, location)
        self.assertEqual(eventScheduleDict, eventSch.toDict())