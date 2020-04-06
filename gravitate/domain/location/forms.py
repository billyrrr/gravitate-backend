import json

from flask_boiler import schema, fields, view_model, view_mediator_dav
from flask_boiler import utils as fb_utils
from google.cloud.firestore_v1 import DocumentSnapshot

from gravitate.domain.driver_navigation.utils import gmaps
from gravitate.domain.location import UserLocation, Location


class LocationFormSchema(schema.Schema):
    coordinates = fields.Raw()
    address = fields.Raw()


class UserLocationFormSchema(LocationFormSchema):

    place_id = fields.Raw()
    user_id = fields.Raw(dump_only=True)
    user_location = fields.Raw(
        missing=fields.allow_missing, load_only=True, required=False)


class UserLocationForm(view_model.ViewModel):

    class Meta:
        schema_cls = UserLocationFormSchema

    @classmethod
    def new(cls, *args, user_id=None, doc_id=None, **kwargs):
        return super().new(
            *args,
            user_location=UserLocation.new(
                user_id=user_id,
                doc_id=doc_id),
            **kwargs
        )

    coordinates = fb_utils.auto_property("coordinates", "user_location")
    address = fb_utils.auto_property("address", "user_location")
    place_id = fb_utils.auto_property("place_id", "user_location")
    user_id = fb_utils.auto_property("user_id", "user_location")

    def propagate_change(self):
        self.user_location.save()


class UserLocationViewMediator(view_mediator_dav.ViewMediatorDeltaDAV):

    class Protocol(view_mediator_dav.ProtocolBase):

        @staticmethod
        def on_create(snapshot: DocumentSnapshot, mediator):
            doc_ref = snapshot.reference
            user_id = doc_ref.parent.parent.id
            doc_id = doc_ref.id
            form = UserLocationForm.new(user_id=user_id, doc_id=doc_id)
            form.update_vals(with_raw=snapshot.to_dict())
            form.propagate_change()

        on_update = on_create


class UserSublocationFormSchema(LocationFormSchema):

    place_id = fields.Raw()
    user_id = fields.Raw()
    user_location = fields.Raw(
        missing=fields.allow_missing, load_only=True, required=False)
    location = fields.Raw(
        missing=fields.allow_missing, load_only=True, required=False)


class UserSublocationForm(view_model.ViewModel):

    class Meta:
        schema_cls = UserSublocationFormSchema

    @classmethod
    def new(cls, *args, doc_id=None, user_location_id=None, **kwargs):
        return super().new(
            *args,
            user_location=UserLocation.get(doc_id=user_location_id),
            location=Location.new(doc_id=doc_id),
            **kwargs
        )

    @property
    def coordinates(self):
        return self.location.coordinates

    def _to_address(self):
        res = gmaps.reverse_geocode(
            latlng=(self.location.coordinates["latitude"],
                    self.location.coordinates["longitude"]),
            result_type=["route",]
        )
        return res[0]["formatted_address"]

    @coordinates.setter
    def coordinates(self, value):
        self.location.coordinates = value
        self.location.address = self._to_address()

    def propagate_change(self):
        self.location.save()
        self.user_location.add_sublocation(
            location_id=self.user_location.doc_id,
            sublocation_ids=[self.location.doc_id]
        )


class UserSublocationViewMediator(view_mediator_dav.ViewMediatorDeltaDAV):

    class Protocol(view_mediator_dav.ProtocolBase):

        @staticmethod
        def on_create(snapshot: DocumentSnapshot, mediator):
            doc_ref = snapshot.reference
            # user_id = doc_ref.parent.parent.parent.parent.id
            doc_id = doc_ref.id
            user_location_id = doc_ref.parent.parent.id
            form = UserSublocationForm.new(
                user_location_id=user_location_id, doc_id=doc_id)
            form.update_vals(with_raw=snapshot.to_dict())
            form.propagate_change()

        on_update = on_create
