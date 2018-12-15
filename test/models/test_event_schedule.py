import unittest

from gravitate.controllers import eventscheduleutils
from gravitate.models import EventSchedule
from test import factory
from test.test_event_schedule_utils import eventScheduleDict


class EventScheduleDaoTest(unittest.TestCase):

    def testFromAndToDict(self):
        eventSchedule = EventSchedule.fromDict(eventScheduleDict)
        self.assertDictEqual(eventScheduleDict, eventSchedule.toDict())

    def testCreate(self):
        rideRequest = factory.getMockRideRequest()
        eventSch = eventscheduleutils.buildEventSchedule(rideRequest)
        self.assertEqual(eventScheduleDict, eventSch.toDict())