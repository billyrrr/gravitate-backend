from unittest import TestCase

from gravitate import main
from gravitate.domain.location import UserLocation
from gravitate.domain.location.models import LocationFactory


class RequestRideTest(TestCase):
    ride_request_ids_to_delete = list()

    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()
        self.userIds = ["testuid1", "testuid2"]
        self.from_location = LocationFactory.from_pickup_address("Tenaya Hall, San Diego, CA 92161")
        self.from_location.save()
        self.to_location = LocationFactory.from_pickup_address("Tioga Hall, San Diego, CA 92161")
        self.to_location.save()

    def testCreateRideHost(self):

        form = {
            "from_location": self.from_location.doc_ref_str,
            "to_location": self.to_location.doc_ref_str,
            "user_id": "testuid1",
            "earliest_departure": "2014-12-29T03:12:58.019077"
        }

        r = self.app.post(path='/rideHosts', json=form)
        assert r.status_code == 200
        print(r.json)
        print(r)

    def tearDown(self) -> None:
        self.from_location.delete()
        self.to_location.delete()