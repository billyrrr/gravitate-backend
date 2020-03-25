import time
from unittest import TestCase

from google.cloud.firestore_v1 import Query

from gravitate import main
from gravitate.domain.bookings import RiderBooking
from gravitate.domain.host_car import RideHost
from gravitate.domain.location import UserLocation
from gravitate.domain.location.models import LocationFactory
from gravitate.domain.matcher.orbit import Orbit, OrbitViewMediator, OrbitView
from gravitate.domain.matcher.timeline import Timeline
from gravitate.domain.target import Target


class CreateTimelineTest(TestCase):
    ride_request_ids_to_delete = list()

    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()
        self.userIds = ["testuid1", "testuid2"]
        self.from_location = LocationFactory.from_pickup_address("Tenaya Hall, San Diego, CA 92161")
        self.from_location.save()
        self.to_location = LocationFactory.from_pickup_address("Tioga Hall, San Diego, CA 92161")
        self.to_location.save()

        self.ride_host = RideHost.new(
            doc_id="tmp_ride_host_1",
            earliest_departure=1419851578,
            from_location=self.from_location,
            to_location=self.to_location,
            user_id="testuid1",
            status="created"
        )

        self.ride_host.save()

        self.rider_booking = RiderBooking.new(
            doc_id="tmp_rider_booking_1",
            earliest_departure=1419851578,
            from_location=self.from_location,
            to_location=self.to_location,
            user_id="xHU5Hp8OJbVitZEWPlWk3VGyC8I3",
            status="created"
        )

        self.rider_booking.save()

    def testCreateTimeline(self):
        orbit_id = Orbit.create_one()
        Orbit.add_rider(
            orbit_id=orbit_id, booking_id=self.rider_booking.doc_id)
        obj = Orbit.get(doc_id=orbit_id)
        Orbit.add_host(
            orbit_id=orbit_id, hosting_id=self.ride_host.doc_id
        )
        obj = Orbit.get(doc_id=orbit_id)
        timeline = Timeline.new(orbit=obj)

        print(timeline.timeline)

    # def test_generate_view(self):
    #     hosting_mediator = OrbitViewMediator(
    #         query=Query(parent=Orbit._get_collection())
    #     )
    #
    #     hosting_mediator.start()
    #
    #     time.sleep(5)

    def tearDown(self) -> None:
        self.from_location.delete()
        self.to_location.delete()
        self.ride_host.delete()
        self.rider_booking.delete()
