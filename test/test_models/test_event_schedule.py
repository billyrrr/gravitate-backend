import unittest

import test.store.model
from gravitate.domain.event_schedule import actions as event_schedule_actions
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
        event_sch = event_schedule_actions.create_event_schedule(ride_request, location)

        d = event_schedule_dict.copy()
        d.pop("locationRef")
        d.pop("destTime")

        self.assertEqual(event_sch.destTime, 1545069600, "destTime should be set for sorting purposes")
        self.assertIsNotNone(event_sch.locationRef, "locationRef should not be none. ")

        self.assertDictContainsSubset(d, event_sch.to_dict())
