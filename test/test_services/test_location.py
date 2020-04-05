from unittest import TestCase

from flask_boiler import testing_utils
from flask_boiler.context import Context as CTX
from google.cloud import firestore

from gravitate import main
from gravitate.domain.location import UserLocation
from gravitate.domain.location.forms import UserLocationForm


class CreateUserLocationTest(TestCase):

    def setUp(self):
        self.user_id = "user_id_1"
        self.doc_id = "test_doc_id_1"
        self.expected_path = "users/user_id_1/locations_POST/test_doc_id_1"
        self.app = main.app.test_client()  # to make sure that main is run

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
        assert d.items() >= {
            'coordinates': {'latitude': 32.8794203,
                            'longitude': -117.2428555},
            'address': 'Tenaya Hall, San Diego, CA 92161',
            'placeId': 'test_place_id_1'
        }.items()

    def test_new(self):
        _ = UserLocationForm.new(
            user_id=self.user_id,
            doc_id=self.doc_id
        )

    def tearDown(self) -> None:
        CTX.db.document(self.expected_path).delete()
        UserLocation.ref_from_id(self.doc_id).delete()
