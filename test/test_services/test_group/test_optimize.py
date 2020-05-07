import json
import unittest
from unittest import TestCase

# from gravitate import main
from google.cloud.firestore_v1 import DocumentReference, DocumentSnapshot
from marshmallow.utils import is_iterable_but_not_string

from gravitate import CTX
from gravitate.algo_server import TargetRepo, RiderTargetMediator, \
    HostTargetSearchMediator
from gravitate.domain.bookings import RiderBooking, RiderTarget
from gravitate.domain.host_car import RideHost
from gravitate.domain.location.models import LocationFactory, Sublocation
from gravitate.domain.matcher.orbit import Orbit, OrbitView
from gravitate.domain.matcher.timeline import Timeline

from flask_boiler import fields, testing_utils

from gravitate.domain.user_new import User


class CreateTimelineTest(TestCase):
    ride_request_ids_to_delete = list()

    def setUp(self):
        # main.app.testing = True
        # self.app = main.app.test_client()
        self.userIds = ["testuid1", "testuid2"]
        self.users = {
            user_id: User.new(doc_id=user_id, name="My Name",
                              email=f"{user_id}@myemail.com")
            for user_id in self.userIds
        }
        _ = [user.save() for _, user in self.users.items()]

        self.host_from = LocationFactory.from_place_address(
            "8775 Costa Verde Blvd, San Diego, CA 92122")
        self.host_from.user_id = self.userIds[0]
        self.host_from.save()

        self.host_to = LocationFactory.from_place_address(
            "Center Hall, San Diego, CA")
        self.host_to.user_id = self.userIds[0]
        self.host_to.save()

        self.rider_from = LocationFactory.from_place_address(
            "3915 Nobel Drive, San Diego, CA")
        a = Sublocation.get_with_latlng(
            latitude=self.rider_from.coordinates["latitude"],
            longitude=self.rider_from.coordinates["longitude"])
        a.save()
        self.a = a
        self.rider_from.sublocations = [a.doc_ref]
        self.rider_from.user_id = self.userIds[1]
        self.rider_from.save()

        self.rider_to = LocationFactory.from_place_address(
            "Center Hall, San Diego, CA")
        b = Sublocation.get_with_latlng(
            latitude=self.rider_to.coordinates["latitude"],
            longitude=self.rider_to.coordinates["longitude"])
        b.save()
        self.b = b
        self.rider_to.sublocations = [b.doc_ref]
        self.rider_to.user_id = self.userIds[1]
        self.rider_to.save()

        self.ride_host = RideHost.new(
            doc_id="tmp_ride_host_1",
            earliest_departure=fields.timestamp_from_local_time(
                "2020-04-09T10:55:00"),
            from_location=self.host_from,
            to_location=self.host_to,
            user_id=self.userIds[0],
            status="created"
        )

        self.ride_host.save()

        self.rider_booking = RiderBooking.new(
            doc_id="tmp_rider_booking_1",
            earliest_departure=fields.timestamp_from_local_time(
                "2020-04-09T11:00:00"),
            from_location=self.rider_from,
            to_location=self.rider_to,
            user_id=self.userIds[1],
            status="created"
        )

        self.rider_booking.save()

    def testMatch(self):
        from gravitate.main import orbit_view_mediator
        from gravitate.algo_server import booking_target_mediator

        orbit_view_mediator.start()

        booking_target_mediator.start()

        target_repo = TargetRepo()
        rider_target_mediator = RiderTargetMediator(
            target_repo=target_repo,
            query=RiderTarget.get_query()
        )
        rider_target_mediator.start()

        testing_utils._wait()  # Necessary

        host_target_search_mediator = HostTargetSearchMediator(
            target_repo=target_repo,
            query=RideHost.get_query()
        )
        host_target_search_mediator.start()

        testing_utils._wait(factor=10)

        # for _doc in CTX.db.collection("Orbit").stream():
        #     doc = _doc
        #     break
        # else:
        #     raise
        #
        # view = OrbitView.new(snapshot=doc)
        # is_iterable_but_not_string(view)

        for doc in CTX.db.collection(
                f"users/{self.userIds[1]}/bookings/{self.rider_booking.doc_id}/orbits").stream():
            assert isinstance(doc, DocumentSnapshot)
            print(doc.to_dict())
            # assert False
            json.dumps(doc.to_dict())
            break
        else:
            # Should contain at least one element
            assert False

    def testCreateTrip(self):

        orbit_id = Orbit.create_one()

        Orbit.match(
            orbit_id=orbit_id,
            hosting_id=self.ride_host.doc_id,
            rider_records=[
                (self.rider_booking.doc_id,
                 self.a.doc_id,
                 self.b.doc_id)
            ]
        )

        testing_utils._wait()

        CTX._enable_logging()
        from gravitate.domain.matcher.orbit import OrbitTripMediator

        orbit_trip_mediator = OrbitTripMediator(query=Orbit.get_query())
        orbit_trip_mediator.start()

        testing_utils._wait(factor=2)

        order_path = f"orders/{self.rider_booking.doc_id}"
        order_doc_ref: DocumentReference = CTX.db.document(order_path)
        assert order_doc_ref.get().to_dict() == {
            'created_at': '2020-05-06T15:13:17Z',
            'driver': {'device_id': '',
                       'id': 'testuid1',
                       'name': 'My Name',
                       'phone_number': '',
                       'role': 'driver'},
            'dropoff': {'address': 'Library Walk',
                        'latitude': 32.877622,
                        'longitude': -117.2375391},
            'pickup': {'address': '3915-3927',
                       'latitude': 32.8683701,
                       'longitude': -117.2221759},
            'rider': {'device_id': '',
                      'id': 'testuid2',
                      'name': 'My Name',
                      'phone_number': '',
                      'role': 'rider'},
            'status': 'ACCEPTED',
            'updated_at': '2020-05-06T15:13:17Z'}

        # assert False

        # for _doc in CTX.db.collection("Orbit").stream():
        #     doc = _doc
        #     break
        # else:
        #     raise
        #
        # view = OrbitView.new(snapshot=doc)
        # is_iterable_but_not_string(view)

        # for doc in CTX.db.collection(f"users/{self.userIds[1]}/bookings/{self.rider_booking.doc_id}/orbits").stream():
        #     assert isinstance(doc, DocumentSnapshot)
        #     print(doc.to_dict())
        #     # assert False
        #     json.dumps(doc.to_dict())
        #     break
        # else:
        #     # Should contain at least one element
        #     assert False

    def testCreateTimeline(self):
        orbit_id = Orbit.create_one()
        Orbit.add_rider(
            orbit_id=orbit_id, booking_id=self.rider_booking.doc_id,
            pickup_sublocation_id=self.a.doc_id,
            dropoff_sublocation_id=self.b.doc_id
        )
        # obj = Orbit.get(doc_id=orbit_id)
        Orbit.add_host(
            orbit_id=orbit_id, hosting_id=self.ride_host.doc_id
        )
        obj = Orbit.get(doc_id=orbit_id)
        timeline = Timeline.new(orbit=obj)

        timeline._directions()

    #
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

        testing_utils._delete_all(CTX=CTX, collection_name="Orbit")
        testing_utils._delete_all(CTX=CTX, subcollection_name="orbits")
        testing_utils._delete_all(CTX=CTX, subcollection_name="bookings")
