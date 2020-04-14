import unittest
from unittest import TestCase

# from gravitate import main
from gravitate.domain.bookings import RiderBooking
from gravitate.domain.host_car import RideHost
from gravitate.domain.location.models import LocationFactory
from gravitate.domain.matcher.orbit import Orbit
from gravitate.domain.matcher.timeline import Timeline

from flask_boiler import fields

class CreateTimelineTest(TestCase):
    ride_request_ids_to_delete = list()

    def setUp(self):
        # main.app.testing = True
        # self.app = main.app.test_client()
        self.userIds = ["testuid1", "testuid2"]

        self.host_from = LocationFactory.from_place_address("8775 Costa Verde Blvd, San Diego, CA 92122")
        self.host_from.save()
        self.host_to = LocationFactory.from_place_address("Center Hall, San Diego, CA")
        self.host_to.save()
        self.rider_from = LocationFactory.from_place_address("3915 Nobel Drive, San Diego, CA")
        self.rider_from.save()
        self.rider_to = LocationFactory.from_place_address(
            "Center Hall, San Diego, CA")
        self.rider_to.save()

        self.ride_host = RideHost.new(
            doc_id="tmp_ride_host_1",
            earliest_departure=fields.timestamp_from_local_time("2020-04-09T10:55:00"),
            from_location=self.host_from,
            to_location=self.host_to,
            user_id="testuid1",
            status="created"
        )

        self.ride_host.save()

        self.rider_booking = RiderBooking.new(
            doc_id="tmp_rider_booking_1",
            earliest_departure=fields.timestamp_from_local_time("2020-04-09T11:00:00"),
            from_location=self.rider_from,
            to_location=self.rider_to,
            user_id="xHU5Hp8OJbVitZEWPlWk3VGyC8I3",
            status="created"
        )

        self.rider_booking.save()

    def testCreateTimeline(self):
        orbit_id = Orbit.create_one()
        Orbit.add_rider(
            orbit_id=orbit_id, booking_id=self.rider_booking.doc_id)
        # obj = Orbit.get(doc_id=orbit_id)
        Orbit.add_host(
            orbit_id=orbit_id, hosting_id=self.ride_host.doc_id
        )
        obj = Orbit.get(doc_id=orbit_id)
        timeline = Timeline.new(orbit=obj)

        timeline._directions()
        assert False

    # def test_generate_view(self):
    #     hosting_mediator = OrbitViewMediator(
    #         query=Query(parent=Orbit._get_collection())
    #     )
    #
    #     hosting_mediator.start()
    #
    #     time.sleep(5)

    def tearDown(self) -> None:
        self.host_from.delete()
        self.host_to.delete()
        self.rider_from.delete()
        self.rider_to.delete()

        self.ride_host.delete()
        self.rider_booking.delete()
