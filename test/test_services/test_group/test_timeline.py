import json
import time
from unittest import TestCase

from flask_boiler import testing_utils
from google.cloud.firestore_v1 import Query

from gravitate import main
from gravitate.domain.bookings import RiderBooking
from gravitate.domain.host_car import RideHost
from gravitate.domain.location import UserLocation
from gravitate.domain.location.models import LocationFactory, Sublocation
from gravitate.domain.matcher.orbit import Orbit, OrbitViewMediator, OrbitView
from gravitate.domain.matcher.timeline import Timeline
from gravitate.domain.target import Target
from gravitate.domain.user_new import User


class CreateTimelineTest(TestCase):
    ride_request_ids_to_delete = list()

    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()
        self.userIds = ["testuid1", "testuid2"]

        self.from_location: UserLocation = LocationFactory.from_pickup_address("Tenaya Hall, San Diego, CA 92161")
        self.from_location.save()

        self.sublocation = Sublocation.get_with_latlng(
            latitude=self.from_location.latitude,
            longitude=self.from_location.longitude
        )
        self.sublocation.save()

        testing_utils._wait()

        UserLocation.add_sublocation_with_id(
            self.from_location.doc_id, [self.sublocation.doc_id],
        )

        self.to_location = LocationFactory.from_pickup_address("Tioga Hall, San Diego, CA 92161")
        self.to_location.save()

        testing_utils._wait()

        UserLocation.add_sublocation_with_id(
            self.to_location.doc_id, [self.sublocation.doc_id]
        )

        self.users = {
            user_id: User.new(doc_id=user_id, name="My Name", email=f"{user_id}@myemail.com")
            for user_id in self.userIds
        }
        _ = [user.save() for _, user in self.users.items()]

        self.ride_host = RideHost.new(
            doc_id="tmp_ride_host_1",
            earliest_departure=1419851578,
            from_location=self.from_location,
            to_location=self.to_location,
            user_id=self.userIds[0],
            status="created"
        )

        self.ride_host.save()

        self.rider_booking = RiderBooking.new(
            doc_id="tmp_rider_booking_1",
            earliest_departure=1419851578,
            from_location=self.from_location,
            to_location=self.to_location,
            user_id=self.userIds[1],
            status="created"
        )

        self.rider_booking.save()

    def testCreateTimeline(self):
        orbit_id = Orbit.create_one()
        Orbit.match(
            orbit_id=orbit_id,
            hosting_id=self.ride_host.doc_id,
            rider_records=[
                (self.rider_booking.doc_id,
                 self.sublocation.doc_id,
                 self.sublocation.doc_id)
            ]
        )

        obj = Orbit.get(doc_id=orbit_id)
        timeline = Timeline.new(orbit=obj)
        print(timeline._directions())
        t = timeline.timeline

        print(json.dumps(t))

        # assert False

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
        _ = [user.delete() for _, user in self.users.items()]
        self.ride_host.delete()
        self.rider_booking.delete()
