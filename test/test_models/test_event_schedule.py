import unittest

import test.store.model
from gravitate.controllers import eventscheduleutils
from gravitate.models import AirportEventSchedule
from test import store

event_schedule_dict = store.eventScheduleDict.copy()


class EventScheduleDaoTest(unittest.TestCase):

    def test_from_and_to_dict(self):
        event_schedule = AirportEventSchedule.from_dict(event_schedule_dict)
        self.assertDictEqual(event_schedule_dict, event_schedule.to_dict())

    def test_create(self):
        ride_request = test.store.model.getMockRideRequest()
        location = test.store.model.getLocation()
        event_sch = eventscheduleutils.create_event_schedule(ride_request, location)
        event_schedule_dict["destTime"] = 1545069600  # .destTime is used off-label for sorting
        self.assertDictEqual(event_schedule_dict, event_sch.to_dict())
