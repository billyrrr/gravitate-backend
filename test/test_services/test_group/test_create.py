from unittest import TestCase

from gravitate import main
from gravitate.domain.bookings import RiderBooking
from gravitate.domain.host_car import RideHost
from gravitate.domain.location import UserLocation
from gravitate.domain.location.models import LocationFactory
from gravitate.domain.matcher.orbit import Orbit
from gravitate.domain.target import Target


class CreateRideHostTest(TestCase):
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
            from_location=self.from_location,
            to_location=self.to_location,
            target=Target.new(),  # Note that target is not saved yet
            user_id="testuid1"
        )

        self.ride_host.save()

        self.rider_booking = RiderBooking.new(
            doc_id="tmp_rider_booking_1",
            from_location=self.from_location,
            to_location=self.to_location,
            target=Target.new(),  # Note that target is not saved yet
            user_id="testuid2"
        )

        self.rider_booking.save()

    def testCreateRideHost(self):
        self.orbit = Orbit.new()

        orbit = self.orbit
        orbit.add_rider(self.rider_booking)
        orbit.add_host(self.ride_host)

    def tearDown(self) -> None:
        self.from_location.delete()
        self.to_location.delete()
