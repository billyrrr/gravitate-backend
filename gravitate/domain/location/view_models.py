from flask_boiler import bpstore, fields, view_model, schema, view
from flask_boiler.struct import Struct, SnapshotStruct
from google.cloud.firestore_v1 import DocumentSnapshot

from . import UserLocation
from ... import CTX


class UserSublocationViewSchema(schema.Schema):
    _id = fields.Raw(dump_only=True, data_key="id")
    place_id = fields.Raw(dump_only=True)
    latitude = fields.Raw(dump_only=True)
    longitude = fields.Raw(dump_only=True)
    address = fields.Raw(dump_only=True)
    sublocations = fields.Raw(dump_only=True)
    place_name = fields.Raw(dump_only=True)


class UserLocationViewStoreSchema(bpstore.BPSchema):

    user_location = fields.StructuralRef(many=False, dm_cls=UserLocation)


class UserLocationView(view_model.ViewModel):

    class Meta:
        schema_cls = UserSublocationViewSchema

    @classmethod
    def new(cls, *args, snapshot=None, **kwargs):
        snapshot_struct = SnapshotStruct(
            schema_cls=UserLocationViewStoreSchema)
        snapshot_struct["user_location"] = (UserLocation, snapshot)
        store = bpstore.BusinessPropertyStore.from_snapshot_struct(
            snapshot_struct=snapshot_struct,
            obj_options=dict(
                must_get=True
            )
        )
        return super().new(*args, store=store, **kwargs)

    @property
    def _id(self):
        return self.doc_ref.id

    @property
    def latitude(self):
        return self.store.user_location.coordinates["latitude"]

    @property
    def longitude(self):
        return self.store.user_location.coordinates["longitude"]

    @property
    def address(self):
        return self.store.user_location.address

    @property
    def place_id(self):
        return self.store.user_location.place_id

    @property
    def doc_ref(self):
        return CTX.db.document(f"users/{self.store.user_location.user_id}/"
                               f"locations/{self.store.user_location.doc_id}")

    @property
    def sublocations(self):
        return [sublocation.to_dict()
                for sublocation in self.store.user_location.sublocations]


class UserLocationViewMediator(view.QueryMediator):

    class Protocol(view.ProtocolBase):

        @staticmethod
        def on_create(snapshot: DocumentSnapshot, mediator):
            obj = UserLocationView.new(snapshot=snapshot)
            mediator.notify(obj=obj)
