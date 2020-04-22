import time
from unittest import TestCase

from gravitate import main, CTX
from gravitate.domain.host_car import RideHost
from gravitate.domain.location import UserLocation
from gravitate.domain.location.models import LocationFactory


class CreateRideHostTest(TestCase):

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

        self.hosting_id_to_delete = list()

    def testCreateRideHost(self):
        doc_id_1 = "test_doc_id_1"

        form = {
            "doc_id": doc_id_1,
            "from_location": self.from_location_1.doc_ref_str,
            "to_location": self.to_location_1.doc_ref_str,
            "user_id": self.userIds[0],
            "earliest_departure": "2014-12-29T03:12:58"
        }

        r = self.app.post(path='/rideHosts', json=form)
        assert r.status_code == 200
        time.sleep(5)

        ref = CTX.db.document("rideHosts/{}".format(doc_id_1))
        d = ref.get().to_dict()

        assert set(d.items()) >= set(
            {'obj_type': 'RideHost', 'userId': 'testuid1',
             'doc_id': 'test_doc_id_1'}.items())

        ref = CTX.db.document(
            "users/{}/hostings/{}".format(self.userIds[0], doc_id_1))
        d = ref.get().to_dict()
        assert d.items() >= {
            'obj_type': 'RideHostReadModel',
            'latest_departure': None,
            'user_id': 'testuid1',
            'localdate_string': '2014-12-29T03:12:58',
            'latest_arrival': None,
            'doc_ref': 'users/testuid1/hostings/test_doc_id_1',
            'earliest_arrival': None}.items()

    def tearDown(self) -> None:
        self.from_location_1.delete()
        self.to_location_1.delete()

        for hosting_id in self.hosting_id_to_delete:
            RideHost.get(doc_id=hosting_id).delete()

