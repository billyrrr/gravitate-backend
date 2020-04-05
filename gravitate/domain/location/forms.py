from flask_boiler import schema, fields, view_model, view_mediator_dav
from flask_boiler import utils as fb_utils
from google.cloud.firestore_v1 import DocumentSnapshot

from gravitate.domain.location import UserLocation


class UserLocationFormSchema(schema.Schema):

    coordinates = fields.Raw()
    address = fields.Raw()
    place_id = fields.Raw()
    user_id = fields.Raw()
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
