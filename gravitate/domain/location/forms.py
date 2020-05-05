from flask_boiler import view_model, view
from flask_boiler import utils as fb_utils
from google.cloud.firestore_v1 import DocumentSnapshot

from gravitate.domain.location import UserLocation, Location
from gravitate.domain.location.models import Sublocation
from gravitate.domain.location.schema import UserLocationFormSchema, \
    UserSublocationFormSchema


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

    @property
    def latitude(self):
        return self.user_location.coordinates["latitude"]

    @latitude.setter
    def latitude(self, value):
        self.user_location.coordinates["latitude"] = value

    @property
    def longitude(self):
        return self.user_location.coordinates["longitude"]

    @longitude.setter
    def longitude(self, value):
        self.user_location.coordinates["longitude"] = value

    address = fb_utils.auto_property("address", "user_location")
    place_id = fb_utils.auto_property("place_id", "user_location")
    place_name = fb_utils.auto_property("place_name", "user_location")
    user_id = fb_utils.auto_property("user_id", "user_location")

    def propagate_change(self):
        self.user_location.save()


class UserLocationFormMediator(view.QueryMediator):

    def notify(self, obj):
        obj.propagate_change()

    class Protocol(view.ProtocolBase):

        @staticmethod
        def on_create(snapshot: DocumentSnapshot, mediator):
            doc_ref = snapshot.reference
            user_id = doc_ref.parent.parent.id
            doc_id = doc_ref.id
            form = UserLocationForm.new(user_id=user_id, doc_id=doc_id)
            form.update_vals(with_raw=snapshot.to_dict())
            mediator.notify(obj=form)
            snapshot.reference.delete()

        on_update = on_create


class UserSublocationForm(view_model.ViewModel):

    class Meta:
        schema_cls = UserSublocationFormSchema

    @classmethod
    def new(cls, *args, doc_id=None, user_location_id=None, **kwargs):
        return super().new(
            *args,
            user_location=UserLocation.get(doc_id=user_location_id),
            location=Sublocation.new(doc_id=doc_id),
            **kwargs
        )

    @property
    def latitude(self):
        return self.location.coordinates["latitude"]

    @latitude.setter
    def latitude(self, value):
        self.location.coordinates["latitude"] = value

    @property
    def longitude(self):
        return self.location.coordinates["longitude"]

    @longitude.setter
    def longitude(self, value):
        self.location.coordinates["longitude"] = value

    def propagate_change(self):
        self.location.save()
        UserLocation.add_sublocation(
            location_id=self.user_location.doc_id,
            sublocation_ids=[self.location.doc_id]
        )


class UserSublocationFormMediator(view.QueryMediator):

    def notify(self, obj):
        obj.propagate_change()

    class Protocol(view.ProtocolBase):

        @staticmethod
        def on_create(snapshot: DocumentSnapshot, mediator):
            doc_ref = snapshot.reference
            # user_id = doc_ref.parent.parent.parent.parent.id
            doc_id = doc_ref.id
            user_location_id = doc_ref.parent.parent.id
            form = UserSublocationForm.new(
                user_location_id=user_location_id, doc_id=doc_id)
            form.update_vals(with_raw=snapshot.to_dict())
            mediator.notify(obj=form)
            snapshot.reference.delete()

        on_update = on_create
