from unittest import TestCase

from flask_boiler import testing_utils
from flask_boiler.context import Context as CTX
from google.cloud import firestore

from gravitate import main
from gravitate.domain.location import UserLocation, Location
from gravitate.domain.location.forms import UserLocationForm, \
    UserSublocationForm


class CreateUserLocationTest(TestCase):

    def setUp(self):
        self.user_id = "user_id_1"
        self.doc_id = "test_doc_id_1"
        self.expected_path = "users/user_id_1/locations_POST/test_doc_id_1"
        self.app = main.app.test_client()  # to make sure that main is run
        testing_utils._wait()

    def test_create(self):
        doc_ref: firestore.DocumentReference = \
            CTX.db.document(self.expected_path)
        form = {
            'coordinates': {'latitude': 32.8794203,
                            'longitude': -117.2428555},
            'address': 'Tenaya Hall, San Diego, CA 92161',
            'placeId': 'test_place_id_1',
        }
        doc_ref.create(
            document_data=form
        )
        testing_utils._wait()
        user_location = UserLocation.get(doc_id=self.doc_id)
        d = user_location.to_dict()
        assert d == {'obj_type': 'UserLocation', 'placeId': 'test_place_id_1',
                     'sublocations': [], 'doc_id': 'test_doc_id_1',
                     'userId': 'user_id_1',
                     'doc_ref': 'locations/test_doc_id_1',
                     'coordinates': {'longitude': -117.2428555,
                                     'latitude': 32.8794203},
                     'address': 'Tenaya Hall, San Diego, CA 92161'}

    def test_new(self):
        _ = UserLocationForm.new(
            user_id=self.user_id,
            doc_id=self.doc_id
        )

    def tearDown(self) -> None:
        CTX.db.document(self.expected_path).delete()
        UserLocation.ref_from_id(self.doc_id).delete()


class CreateUserSublocationTest(TestCase):

    def setUp(self):
        self.user_id = "user_id_1"
        self.user_location_id = "test_doc_id_1"
        self.doc_id = "sublocation_id"
        self.user_location_path = "users/user_id_1/" \
                                  "locations_POST/test_doc_id_1"
        self.expected_path = "users/user_id_1/" \
                             "locations_POST/test_doc_id_1/" \
                             f"sublocations_POST/{self.doc_id}"
        self.app = main.app.test_client()  # to make sure that main is run
        testing_utils._wait()

    def test_create(self):
        doc_ref = CTX.db.document(self.user_location_path)
        doc_ref.set(
            document_data={'obj_type': 'UserLocation',
                           'placeId': 'test_place_id_1', 'sublocations': [],
                           'doc_id': 'test_doc_id_1', 'userId': 'user_id_1',
                           'doc_ref': 'locations/test_doc_id_1',
                           'coordinates': {'longitude': -117.2428555,
                                           'latitude': 32.8794203},
                           'address': 'Tenaya Hall, San Diego, CA 92161'}
        )

        testing_utils._wait()

        sublocation_ref = CTX.db.document(self.expected_path)
        sublocation_ref.create(
            document_data={
                'coordinates': {'latitude': 32.87952213052025,
                                'longitude': -117.2436009719968},
            }
        )

        # Tests that a new location is created
        testing_utils._wait()
        location = Location.get(doc_id=self.doc_id)
        d = location.to_dict()
        assert d == {'coordinates': {'longitude': -117.2436009719968, 'latitude': 32.87952213052025}, 'doc_id': 'sublocation_id', 'obj_type': 'Location', 'doc_ref': 'locations/sublocation_id', 'address': 'Scholars Dr S, San Diego, CA 92161, USA'}

        # Tests that the new location is registered as a sublocation
        #       of the parent UserLocation
        user_location = UserLocation.get(doc_id=self.user_location_id)
        d = user_location.to_dict()
        assert d["sublocations"] == [location.doc_ref]

    def test_new(self):
        obj = UserSublocationForm.new(
            doc_id=self.doc_id,
            user_location_id=self.user_location_id
        )
        obj.coordinates = {'latitude': 32.87952213052025,
                           'longitude': -117.2436009719968}
        testing_utils._wait(1)
        assert obj.location.address == \
               "Scholars Dr S, San Diego, CA 92161, USA"

    def tearDown(self) -> None:
        CTX.db.document(self.user_location_path).delete()
        UserLocation.ref_from_id(self.user_location_id).delete()
        CTX.db.document(self.expected_path).delete()
