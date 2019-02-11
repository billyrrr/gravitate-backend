from unittest import TestCase

from gravitate import main

from gravitate import models
from gravitate import data_access
from gravitate.domain.request_ride import builders as ride_request_builders

from test import store
from test.test_main import getMockAuthHeaders


class RequestRideTest(TestCase):
    ride_request_ids_to_delete = list()
    refs_to_delete = list()

    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()
        self.userIds = ["testuid1", "testuid2"]

        location_dict = store.getLocationDict(location_category="social")
        location = models.Location.from_dict(location_dict)
        location_ref = data_access.LocationGenericDao().create(location)
        self.refs_to_delete.append(location_ref)

        event_dict = store.getEventDict(event_category="social")
        event_dict["locationRef"] = location_ref
        event = models.Event.from_dict(event_dict)
        event_ref = data_access.EventDao().create(event)
        self.refs_to_delete = list()
        self.refs_to_delete.append(event_ref)

        event_id = event_ref.id
        self.d = store.EventRideRequestFormDictFactory().create(event_id=event_id)
        self.ride_request_ids_to_delete = list()

    def testCreateRideRequestsTemp(self):

        # Create new rideRequests
        for userId in self.userIds:
            form = self.d
            form["testUserId"] = userId
            r = self.app.post(  # TODO: change everywhere to json=form (used to be json=json.dumps(form))
                path='/requestRide/event', json=form, headers=getMockAuthHeaders(userId))
            print(r.json)
            self.assertIn("firestoreRef", r.json.keys())
            rid = r.json["id"]
            ride_request = data_access.RideRequestGenericDao().get_by_id(rid)
            print(ride_request.to_dict())
            firestore_ref = ride_request.get_firestore_ref()  # Not that it is actually rideRequestId

            self.ride_request_ids_to_delete.append((userId, firestore_ref.id))

    def tearDown(self):
        """
        Deletes all rideRequests created by the test
        :return:
        """
        for uid, rid in self.ride_request_ids_to_delete:
            r = self.app.delete(path='/rideRequests' + '/' + rid,
                                headers=getMockAuthHeaders(uid=uid)
                                )
            assert r.status_code == 200
        self.ride_request_ids_to_delete.clear()

        for ref in self.refs_to_delete:
            ref.delete()
        self.refs_to_delete.clear()
