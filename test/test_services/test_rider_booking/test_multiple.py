import sys
from unittest import TestCase

from gravitate import main
from gravitate.domain.bookings import RiderBooking
from gravitate.domain.location import UserLocation
from gravitate.domain.location.models import LocationFactory

import time


class CreateRiderBookingTest(TestCase):
    ride_request_ids_to_delete = list()

    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()
        self.userIds = ["testuid1", "testuid2"]

        self.from_location_1 = LocationFactory.from_pickup_address("Tenaya Hall, San Diego, CA 92161")
        self.from_location_1.user_id = self.userIds[0]
        self.from_location_1.save()
        self.to_location_1 = LocationFactory.from_pickup_address("Tioga Hall, San Diego, CA 92161")
        self.to_location_1.user_id = self.userIds[0]
        self.to_location_1.save()

        self.from_location_2 = LocationFactory.from_pickup_address(
            "Tenaya Hall, San Diego, CA 92161")
        self.from_location_2.user_id = self.userIds[1]
        self.from_location_2.save()
        self.to_location_2 = LocationFactory.from_pickup_address(
            "Tioga Hall, San Diego, CA 92161")
        self.to_location_2.user_id = self.userIds[1]
        self.to_location_2.save()

        self.booking_id_to_delete = list()

    def testCreateRiderBooking(self):

        form = {
            "doc_id": "rider_booking_id_2",
            "from_location": self.from_location_1.doc_ref_str,
            "to_location": self.to_location_1.doc_ref_str,
            "user_id": "testuid1",
            "earliest_departure": "2014-12-29T03:12:58.019077"
        }

        # Creates a rider booking
        r = self.app.post(path='/riderBookings', json=form)

        assert r.status_code == 200
        doc_id = r.json["booking_id"]
        self.booking_id_to_delete.append(doc_id)

        time.sleep(5)

        form = {
            "doc_id": "rider_booking_id_3",
            "from_location": self.from_location_2.doc_ref_str,
            "to_location": self.to_location_2.doc_ref_str,
            "user_id": "testuid1",
            "earliest_departure": "2014-12-29T03:12:58.019077"
        }

        # Creates a rider booking
        r = self.app.post(path='/riderBookings', json=form)
        assert r.status_code == 200
        doc_id = r.json["booking_id"]
        self.booking_id_to_delete.append(doc_id)

        time.sleep(5)

    def tearDown(self) -> None:
        self.from_location_1.delete()
        self.to_location_1.delete()
        self.from_location_2.delete()
        self.to_location_2.delete()

        for booking_id in self.booking_id_to_delete:
            RiderBooking.get(doc_id=booking_id).delete()

