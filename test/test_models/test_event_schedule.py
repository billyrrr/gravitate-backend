import unittest

import test.factory.model
from gravitate.controllers import eventscheduleutils
from gravitate.models import AirportEventSchedule
from test import factory
from test.factory import eventScheduleDict


class EventScheduleDaoTest(unittest.TestCase):

    def testFromAndToDict(self):
        eventSchedule = AirportEventSchedule.from_dict(eventScheduleDict)
        self.assertDictEqual(eventScheduleDict, eventSchedule.to_dict())

    def testCreate(self):
        rideRequest = test.factory.model.getMockRideRequest()
        location = test.factory.model.getLocation()
        eventSch = eventscheduleutils.buildEventSchedule(rideRequest, location)
        self.assertEqual(eventScheduleDict, eventSch.to_dict())